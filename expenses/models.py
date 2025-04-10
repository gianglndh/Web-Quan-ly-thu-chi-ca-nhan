from django.db import models
from datetime import date 
from django.contrib.auth.models import User

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Thu nhập'),
        ('expense', 'Chi tiêu'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, verbose_name="Loại giao dịch")
    amount = models.DecimalField(max_digits=20, decimal_places=0, verbose_name="Số tiền")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    date = models.DateField(default=date.today, verbose_name="Ngày giao dịch")

    

    class Meta:
        ordering = ['-date']  

    def __str__(self):
        return f"{self.get_type_display()} - {self.amount} VND ({self.date})"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
