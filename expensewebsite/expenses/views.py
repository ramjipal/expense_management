from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.urls import reverse
# Create your views here.
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
from userpreferences.models import UserPreference, Budget
import datetime


def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    
    exist = UserPreference.objects.filter(user=request.user).exists()
    if not exist:
        messages.warning(request, 'Please set your currency preference first.')
        return redirect(reverse('preferences'))
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'expenses/index.html', context)


@login_required(login_url='/authentication/login')
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/add_expense.html', context)

        Expense.objects.create(owner=request.user, amount=amount, date=date,
                               category=category, description=description)
        messages.success(request, 'Expense saved successfully')

        return redirect('expenses')


@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit-expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit-expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense. date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('expenses')


def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')


def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}
    print(expenses)
    def get_category(expense):
        return expense.category
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount
        return amount

    for y in category_list:
        finalrep[y] = get_expense_category_amount(y)
    return JsonResponse({'expense_category_data': finalrep}, safe=False)

import datetime
from django.http import JsonResponse

def get_expense_by_date(request):
    curr_year = datetime.date.today().year
    curr_month = datetime.date.today().month
    curr_month_expense = Expense.objects.filter(
        owner=request.user, date__year=curr_year, date__month=curr_month).order_by('date')
    expense_dic = {}

    for cmx in curr_month_expense:
        date_str = cmx.date.strftime('%Y-%m-%d')  # Convert date to string
        if date_str in expense_dic:
            expense_dic[date_str] += cmx.amount
        else:
            expense_dic[date_str] = cmx.amount

    return JsonResponse({'expense_by_date': expense_dic}, safe=False)

def get_expense_by_month(request):
    all_expenses = Expense.objects.filter(
        owner=request.user).order_by('date')
    month_dic = {}

    for cmx in all_expenses:
        month = cmx.date.strftime('%B')  # Convert date month to string
        if month in month_dic:
            month_dic[month] += cmx.amount
        else:
            month_dic[month] = cmx.amount

    return JsonResponse({'expense_by_month': month_dic}, safe=False)

def monthSpendBudget(request):
    curr_month = datetime.datetime.today().month
    curr_year = datetime.datetime.today().year
    total_expense = 0
    userbudget = Budget.objects.filter(user = request.user)[:1].get()
    budget = userbudget.budget
    expense = Expense.objects.filter(owner = request.user, date__year = curr_year, date__month = curr_month)
    for ex in expense:
        total_expense+=ex.amount
    return JsonResponse({'monthly_expense': total_expense, 'budget': budget}, safe=False)

 
    



        
        
        
def stats_view(request):
    return render(request, 'expenses/stats.html')



import csv
def export_csv(request):
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = 'attachment; filename = Expenses' + \
        str(datetime.datetime.now())+ '.csv'
    
    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])
    
    expenses = Expense.objects.filter(owner = request.user)
    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])
        
    return response
    
    

# from django.template.loader import render_to_string
# from weasyprint import HTML
# import tempfile
# from django.db.models import Sum
# import os

# os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")

# def export_pdf(request):
#     response = HttpResponse(content_type = 'application/pdf')
#     response['Content-Disposition'] = 'inline; attachment; filename = Expenses' + \
#         str(datetime.datetime.now())+ '.pdf'
        
#     response['Content-Transfer-Encoding'] = 'binary'
#     expenses = Expense.objects.filter(owner = request.user)
    
#     sum = expenses.aggregate(Sum('amount'))
#     html_string = render_to_string(
#         'expenses/pdf-output.html', {'expenses': expenses, 'total': sum['amount_sum']})
#     import os

#     os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")
#     html = HTML(string=html_string)
    
#     result = html.writ_pdf()
    
#     with tempfile.NamedTemporaryFile(delete = True) as output:
#         output.write(result)
#         output.flush()
        
#         output = open(output.name, 'rb')
#         response.write(output.read())
        
#     return response
    


if __name__== "__main__":
    js = get_expense_by_date("ram")
