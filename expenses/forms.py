from django import forms
from .models import Transaction
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu'
        })
    )
    password_confirm = forms.CharField(
        label="Nhập lại mật khẩu",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tên đăng nhập'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
        }
        labels = {
            'username': 'Tên đăng nhập',
            'email': 'Email',
            'password': 'Mật khẩu'
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "❌ Mật khẩu không khớp!")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Mã hóa mật khẩu
        if commit:
            user.save()
        return user
            
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
