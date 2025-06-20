from django.urls import path
from . import views
from . import message_views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about_us'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='logout'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('doctor-login/', views.doctor_login, name='doctor_login'),
    path('staff-login/', views.staff_login, name='staff_login'),
    path('admin-profile/', views.admin_profile, name='admin_profile'),
    path('doctor-profile/', views.doctor_profile, name='doctor_profile'),
    path('staff-profile/', views.staff_profile, name='staff_profile'),
    path('patient-profile/', views.patient_profile, name='patient_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('take-appointment/', views.take_appointment, name='take_appointment'),
    path('available-doctors/', views.available_doctors, name='available_doctors'),
    path('update-appointment-status/<int:appointment_id>/', views.update_appointment_status, name='update_appointment_status'),
    
    # Doctor Management
    path('view-doctors/', views.view_doctors, name='view_doctors'),
    path('add-doctor/', views.add_doctor, name='add_doctor'),
    path('edit-doctor/<int:doctor_id>/', views.edit_doctor, name='edit_doctor'),
    path('delete-doctor/<int:doctor_id>/', views.delete_doctor, name='delete_doctor'),
    
    # Staff Management
    path('view-staffs/', views.view_staffs, name='view_staffs'),
    path('add-staff/', views.add_staff, name='add_staff'),
    path('edit-staff/<int:staff_id>/', views.edit_staff, name='edit_staff'),
    path('delete-staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    
    # Patient Management
    path('register/', views.patient_registration, name='patient_registration'),
    path('manage-patient-profile/', views.manage_patient_profile, name='manage_patient_profile'),
    path('edit-patient/<int:patient_id>/', views.edit_patient, name='edit_patient'),
    path('delete-patient/<int:patient_id>/', views.delete_patient, name='delete_patient'),
    path('view-patient-records/<int:patient_id>/', views.view_patient_records, name='view_patient_records'),
    
    # Records Management
    path('records/', views.view_record, name='view_record'),
    path('get-record-details/<int:record_id>/', views.get_record_details, name='get_record_details'),
    path('add-record/', views.add_record, name='add_record'),
    path('edit-record/<int:record_id>/', views.edit_record, name='edit_record'),
    path('update-record/<int:record_id>/', views.update_record, name='update_record'),
    
    # User Settings
    path('change-password/', views.change_password, name='change_password'),
    
    # Username validation
    path('check-username/', views.check_username, name='check_username'),
    
    # Pending Changes
    path('pending-changes/', views.pending_changes, name='pending_changes'),
    path('approve-change/<int:change_id>/', views.approve_change, name='approve_change'),
    path('reject-change/<int:change_id>/', views.reject_change, name='reject_change'),
    path('get-change-details/<int:change_id>/', views.get_change_details, name='get_change_details'),
    
    # Messaging System
    path('inbox/', message_views.inbox, name='inbox'),
    path('compose-message/', message_views.compose_message, name='compose_message'),
    path('view-message/<int:message_id>/', message_views.view_message, name='view_message'),
    path('delete-message/<int:message_id>/', message_views.delete_message, name='delete_message'),
]