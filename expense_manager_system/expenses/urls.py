from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('expense_list/', views.expense_list, name='expense_list'),
    path('add/', views.add_expense, name='add_expense'),
    path('invoice/<int:expense_id>/', views.generate_invoice, name='generate_invoice'),  
    path('ai-suggestions/', views.ai_suggestions, name='ai_suggestions'),
]