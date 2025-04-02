import os
from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from django.conf import settings


# Generate a key (do this once and store it securely)
# key = Fernet.generate_key()
# print(key.decode())  # Store this key securely

# Use the key from your environment or settings
key = os.environ.get('FERNET_KEY', '-fIhwrpIQzCAVyCkQckinVDc_G9sYohZAf7xGGY4iQA=')  # Replace with your key
cipher = Fernet(key)

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='expense_files/', blank=True, null=True)

    def save(self, *args, **kwargs):
        #Encrypt sensitive fields before saving
        self.title = cipher.encrypt(self.title.encode()).decode()
        self.description = cipher.encrypt(self.description.encode()).decode()
        super().save(*args, **kwargs)

    def decrypt_fields(self):
        #Decrypt fields when accessing
        self.title = cipher.decrypt(self.title.encode()).decode()
        self.description = cipher.encrypt(self.description.encode()).decode()

    def __str__(self):
        return self.title