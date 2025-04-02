from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import Expense
from .forms import ExpenseForm
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync 
from django.core.paginator import Paginator
from django.db.models import Q
import openai


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('expense_list')  # Redirect to the expense list after login
    else:
        form = AuthenticationForm()
    return render(request, 'templates/expenses/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def expense_list(request):
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort_by', 'date')
    filter_by = request.GET.get('filter_by', '')

    expenses = Expense.objects.filter(user=request.user)

    if query:
        expenses = expenses.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if filter_by:
        expenses = expenses.filter(category=filter_by)  # Assuming you have a category field

    expenses = expenses.order_by(sort_by)

    paginator = Paginator(expenses, 10)  # Show 10 expenses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    
    #Decrypting fields for display
    for expense in page_obj:
        expense.decrypt_fields()

    return render(request, 'templates/expenses/expense_list.html', {'page_obj': page_obj, 'query': query})

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()

            # Broadcast the new expense to all connected clients
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "expenses",
                {
                    "type": "expense_update",
                    "data": {
                        "id": expense.id,
                        "title": expense.title,
                        "amount": str(expense.amount),
                        "date": expense.date.strftime('%Y-%m-%d'),
                    },
                },
            )

            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'templates/expenses/add_expense.html', {'form': form})


@login_required
def generate_invoice(request, expense_id):
    expense = Expense.objects.get(id=expense_id)
    response = HttpResponse(content_type='application/pdf')
    response['content-Disposition'] = f'attachment; filename="invoice_{expense.id}.pdf"'
    p = canvas.Canvas(response)
    p.drawString(100, 750, f"invoice for {expense.title}")
    p.drawString(100, 730, f"Amount: Ksh{expense.amount}")
    p.drawString(100, 710, f"Date: {expense.date}")
    p.showPage()
    p.save()
    return response

openai.api_key = "your-openai-api-key" # Replace with your OpenAI API key

@login_required
def ai_suggestions(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use the appropriate OpenAI model
            prompt=f"Provide suggestions for managing expenses based on: {user_input}",
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        suggestion = response.choices[0].text.strip()
        return render(request, 'expenses/ai_suggestions.html', {'suggestion': suggestion})
    return render(request, 'templates/expenses/ai_suggestions.html')