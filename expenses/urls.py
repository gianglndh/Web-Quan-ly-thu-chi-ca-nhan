from django.urls import path
from . import views
from .views import transaction_create
from .views import transaction_list
from .views import register
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 🔹 Đăng ký & đăng nhập
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='expenses/login.html'  # 🔧 dùng đúng đường dẫn hiện tại của bạn
    ), name='login'),    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    

    # 🔹 Giao dịch
    path('', views.transaction_list, name='home'),  # ✅ Trang chủ là danh sách giao dịch
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/new/', views.transaction_create, name='transaction_create'),
    path('transactions/<int:pk>/edit/', views.transaction_update, name='transaction_update'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
]
