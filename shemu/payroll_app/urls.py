from django.urls import path 
from . import views 
  
urlpatterns = [ 
    path("", views.employee_list, name="employee_list"), 
    path("employees/new/", views.employee_create, name="employee_create"), 
    path("employees/<int:pk>/edit/", views.employee_update, 
name="employee_update"), 
    path("employees/<int:pk>/delete/", views.employee_delete, 
name="employee_delete"), 
    path("employees/<int:pk>/overtime/", views.employee_add_overtime, 
name="employee_overtime"), 
  
path("payslips/", views.payslip_list, name="payslip_list"), 
path("payslips/<int:pk>/", views.view_payslips, name="view_payslips"), 
]