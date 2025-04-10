from django import forms
from .models import Transaction
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Nhập lại mật khẩu")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Mật khẩu không khớp!")
            
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'amount', 'description', 'date']
        labels = {
            'type': 'Loại giao dịch',
            'amount': 'Số tiền',
            'description': 'Mô tả',
            'date': 'Ngày giao dịch',
        }
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nhập số tiền'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập mô tả'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
