from django.urls import path, include
from . import views

from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name="expenses"),
    path('add-expense', views.add_expense, name="add-expenses"),
    path('edit-expense/<int:id>', views.expense_edit, name="expense-edit"),
    path('expense-delete/<int:id>', views.delete_expense, name="expense-delete"),
    path('search-expenses', csrf_exempt(views.search_expenses),
         name="search_expenses"),
    
    
    path('expense_category_summary', views.expense_category_summary,
         name="expense_category_summary"),
    path('get_expense_by_date', views.get_expense_by_date,
         name="get_expense_by_date"),
    path('get_expense_by_month', views.get_expense_by_month,
         name="get_expense_by_month"),
    
    path('monthSpendBudget', csrf_exempt(views.monthSpendBudget),
         name="monthSpendBudget"),
    
    path('stats', views.stats_view,
         name="stats"),
    
    path('predict_expense/', include('expenseprediction.urls')), 
    
    path('export-csv', views.export_csv, name = 'export-csv')
#     path('export-pdf', views.export_pdf, name = 'export-pdf')
]
