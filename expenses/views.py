import logging
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import RegisterForm
from datetime import date, timedelta  
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from collections import defaultdict
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Transaction, Category
from django.shortcuts import redirect
from .forms import TransactionForm
from dateutil.relativedelta import relativedelta
import json

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)  # Tự động đăng nhập sau khi đăng ký
            return redirect("transaction_list")  # Chuyển hướng về trang chính

    else:
        form = RegisterForm()

    return render(request, "expenses/register.html", {"form": form})

logger = logging.getLogger(__name__)

@login_required(login_url='login')
def transaction_list(request):
    print("🔎 DEBUG - Query Params:", request.GET)  # Kiểm tra request gửi lên

    # 🟢 Lấy toàn bộ giao dịch của user
    all_transactions = Transaction.objects.filter(user=request.user)

    # 🔹 Lọc dữ liệu theo điều kiện từ request
    transactions = all_transactions.order_by("-date", "-id")

    # 🗓 Lọc theo ngày
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        transactions = transactions.filter(date__range=[start_date, end_date])
    elif start_date:
        transactions = transactions.filter(date__gte=start_date)
    elif end_date:
        transactions = transactions.filter(date__lte=end_date)

    # 📌 Lọc theo loại giao dịch (income/expense)
    transaction_type = request.GET.get("type")
    if transaction_type in ["income", "expense"]:
        transactions = transactions.filter(type=transaction_type)

    # 💰 Lọc theo số tiền
    min_amount = request.GET.get("min_amount")
    max_amount = request.GET.get("max_amount")
    if min_amount:
        transactions = transactions.filter(amount__gte=min_amount)
    if max_amount:
        transactions = transactions.filter(amount__lte=max_amount)

    # 🔎 Tìm kiếm theo mô tả hoặc số tiền
    search_query = request.GET.get("q")
    if search_query:
        transactions = transactions.filter(
            Q(description__icontains=search_query) |
            Q(amount__icontains=search_query)
        )

    # ✅ Tính tổng thu nhập, tổng chi tiêu và số dư
    total_income = transactions.filter(type="income").aggregate(Sum("amount"))["amount__sum"] or 0
    total_expense = transactions.filter(type="expense").aggregate(Sum("amount"))["amount__sum"] or 0
    balance = total_income - total_expense

    # 🔹 Xác định tháng đầu tiên & tháng hiện tại từ toàn bộ giao dịch
    first_transaction = all_transactions.order_by("date").first()
    first_month = first_transaction.date.replace(day=1) if first_transaction else date.today().replace(day=1)
    current_month = date.today().replace(day=1)

    # 🟢 Tạo danh sách tháng (từ tháng đầu tiên đến tháng hiện tại)
    month_labels = []
    temp_month = first_month
    while temp_month <= current_month:
        month_labels.append(temp_month.strftime("%m/%Y"))
        temp_month += relativedelta(months=1)  # 🔥 Fix lỗi tính tháng

    # 🔹 Lấy dữ liệu theo tháng (KHÔNG LỌC)
    transactions_by_month = all_transactions.annotate(month=TruncMonth("date")) \
        .values("month", "type") \
        .annotate(total=Sum("amount"))

    # 🎯 Chuẩn bị dữ liệu biểu đồ theo tháng
    monthly_income = {month: 0 for month in month_labels}
    monthly_expense = {month: 0 for month in month_labels}

    for item in transactions_by_month:
        if item["month"]:  # ✅ Kiểm tra tránh lỗi NoneType
            month_label = item["month"].strftime("%m/%Y")
            if item["type"] == "income":
                monthly_income[month_label] += float(item["total"])  # 🔥 Convert Decimal -> float
            else:
                monthly_expense[month_label] += float(item["total"])  # 🔥 Convert Decimal -> float

    # 🔹 Phân trang (5 giao dịch mỗi trang)
    paginator = Paginator(transactions, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # 🔹 Lấy danh sách danh mục
    categories = Category.objects.filter(user=request.user)

    

    return render(request, "expenses/transaction_list.html", {
        "transactions": page_obj,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "categories": categories,
        "monthly_labels": json.dumps(list(monthly_income.keys())),  # ✅ Convert JSON cho JS
        "monthly_income": json.dumps(list(monthly_income.values())),  # ✅ Convert JSON cho JS
        "monthly_expense": json.dumps(list(monthly_expense.values()))  # ✅ Convert JSON cho JS
    })

# 📌 Thêm giao dịch
@login_required
def transaction_create(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, "✅ Giao dịch đã được thêm thành công!")
            return redirect("transaction_list")
    else:
        form = TransactionForm()

    return render(request, "expenses/transaction_form.html", {"form": form})

# 📌 Chỉnh sửa giao dịch
@login_required
def transaction_update(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == "POST":
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Giao dịch đã được cập nhật!")
            return redirect("transaction_list")
    else:
        form = TransactionForm(instance=transaction)

    return render(request, "expenses/transaction_form.html", {"form": form})

# 📌 Xóa giao dịch
@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)

    if not request.user.is_superuser and transaction.user != request.user:
        return HttpResponse("❌ Bạn không có quyền xóa giao dịch này!", status=403)

    if request.method == "POST":
        transaction.delete()
        messages.success(request, "✅ Giao dịch đã bị xóa!")
        return redirect("transaction_list")

    return render(request, "expenses/transaction_confirm_delete.html", {"transaction": transaction})

@login_required(login_url='login')   
def home(request):
    transactions = Transaction.objects.filter(user=request.user)
    return render(request, 'home.html', {'transactions': transactions})