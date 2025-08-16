from django.urls import path
from . import views

urlpatterns = [
    path('', views.claims_list, name='claims_list'),
    path('claim/<int:claim_id>/', views.claim_detail, name='claim_detail'),
    path('claim/<int:claim_id>/flag/', views.flag_claim, name='flag_claim'),
    path('claim/<int:claim_id>/note/', views.add_note, name='add_note'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
