from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count
from django.template.response import TemplateResponse
from django.urls import path
from django.contrib.auth.hashers import make_password
from .models import Doctor, Staff, Patient, Appointment, Record
from .forms import DoctorAdminForm, StaffAdminForm, PatientAdminForm

class CustomAdminSite(admin.AdminSite):
    site_header = 'CAMS Administration'
    site_title = 'CAMS Admin Portal'
    index_title = 'Welcome to CAMS Admin Portal'
    
    def each_context(self, request):
        context = super().each_context(request)
        context.update({
            'author': 'Jubaer Ahamed Bhuiyan',
            'copyright_year': '2024',
        })
        return context

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        # Add any custom ordering here if needed
        return app_list

    def index(self, request, extra_context=None):
        # Get statistics for dashboard
        today = timezone.now().date()
        extra_context = extra_context or {}
        extra_context.update({
            'patient_count': Patient.objects.count(),
            'doctor_count': Doctor.objects.count(),
            'today_appointments': Appointment.objects.filter(appointment_date=today).count(),
            'pending_appointments': Appointment.objects.filter(status='PENDING').count(),
            'recent_appointments': Appointment.objects.filter(
                appointment_date=today
            ).select_related('doctor__user', 'patient__user').order_by('appointment_time')[:5],
            'recent_records': Record.objects.select_related(
                'doctor__user', 'patient__user'
            ).order_by('-created_at')[:5],
            'author': 'Jubaer Ahamed Bhuiyan',
            'copyright_year': '2024',
        })
        return super().index(request, extra_context)

admin_site = CustomAdminSite(name='custom_admin')

class DoctorAdmin(admin.ModelAdmin):
    form = DoctorAdminForm
    list_display = ('get_full_name', 'specialization', 'phone', 'get_email', 'get_appointment_count')
    list_filter = ('specialization', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'specialization', 'phone')
    readonly_fields = ('created_at',)
    
    def get_full_name(self, obj):
        return f"Dr. {obj.user.get_full_name()}"
    get_full_name.short_description = 'Name'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    
    def get_appointment_count(self, obj):
        return obj.appointment_set.count()
    get_appointment_count.short_description = 'Total Appointments'

    def save_model(self, request, obj, form, change):
        if not change:  # Creating new doctor
            user = User.objects.create_user(
                username=form.cleaned_data.get('username'),
                email=form.cleaned_data.get('email'),
                password=form.cleaned_data.get('password1'),
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name')
            )
            obj.user = user
        else:  # Updating existing doctor
            user = obj.user
            user.username = form.cleaned_data.get('username', user.username)
            user.email = form.cleaned_data.get('email', user.email)
            user.first_name = form.cleaned_data.get('first_name', user.first_name)
            user.last_name = form.cleaned_data.get('last_name', user.last_name)
            if form.cleaned_data.get('password1'):
                user.set_password(form.cleaned_data.get('password1'))
            user.save()
        super().save_model(request, obj, form, change)

class StaffAdmin(admin.ModelAdmin):
    form = StaffAdminForm
    list_display = ('get_full_name', 'position', 'phone', 'get_email', 'created_at')
    list_filter = ('position', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'position', 'phone')
    readonly_fields = ('created_at',)
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def save_model(self, request, obj, form, change):
        if not change:  # Creating new staff
            user = User.objects.create_user(
                username=form.cleaned_data.get('username'),
                email=form.cleaned_data.get('email'),
                password=form.cleaned_data.get('password1'),
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name')
            )
            obj.user = user
        else:  # Updating existing staff
            user = obj.user
            user.username = form.cleaned_data.get('username', user.username)
            user.email = form.cleaned_data.get('email', user.email)
            user.first_name = form.cleaned_data.get('first_name', user.first_name)
            user.last_name = form.cleaned_data.get('last_name', user.last_name)
            if form.cleaned_data.get('password1'):
                user.set_password(form.cleaned_data.get('password1'))
            user.save()
        super().save_model(request, obj, form, change)

class PatientAdmin(admin.ModelAdmin):
    form = PatientAdminForm
    list_display = ('get_full_name', 'phone', 'date_of_birth', 'get_email', 'get_appointment_count')
    list_filter = ('created_at', 'date_of_birth')
    search_fields = ('user__first_name', 'user__last_name', 'phone', 'address')
    readonly_fields = ('created_at',)
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    
    def get_appointment_count(self, obj):
        return obj.appointment_set.count()
    get_appointment_count.short_description = 'Total Appointments'

    def save_model(self, request, obj, form, change):
        if not change:  # Creating new patient
            user = User.objects.create_user(
                username=form.cleaned_data.get('username'),
                email=form.cleaned_data.get('email'),
                password=form.cleaned_data.get('password1'),
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name')
            )
            obj.user = user
        else:  # Updating existing patient
            user = obj.user
            user.username = form.cleaned_data.get('username', user.username)
            user.email = form.cleaned_data.get('email', user.email)
            user.first_name = form.cleaned_data.get('first_name', user.first_name)
            user.last_name = form.cleaned_data.get('last_name', user.last_name)
            if form.cleaned_data.get('password1'):
                user.set_password(form.cleaned_data.get('password1'))
            user.save()
        super().save_model(request, obj, form, change)

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'doctor_name', 'appointment_date', 'appointment_time', 'status', 'created_at')
    list_filter = ('status', 'appointment_date', 'doctor', 'created_at')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 
                    'doctor__user__first_name', 'doctor__user__last_name', 'reason')
    date_hierarchy = 'appointment_date'
    readonly_fields = ('created_at',)
    
    def patient_name(self, obj):
        return obj.patient.user.get_full_name()
    patient_name.short_description = 'Patient'
    
    def doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name()}"
    doctor_name.short_description = 'Doctor'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'doctor__user', 'patient__user'
        )

class RecordAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'doctor_name', 'get_date', 'diagnosis', 'created_at')
    list_filter = ('created_at', 'doctor')
    search_fields = ('patient__user__first_name', 'patient__user__last_name',
                    'doctor__user__first_name', 'doctor__user__last_name',
                    'diagnosis', 'prescription', 'notes')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    def patient_name(self, obj):
        return obj.patient.user.get_full_name()
    patient_name.short_description = 'Patient'
    
    def doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name()}"
    doctor_name.short_description = 'Doctor'
    
    def get_date(self, obj):
        return obj.created_at.date()
    get_date.short_description = 'Date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'doctor__user', 'patient__user'
        )

# Register all models with the custom admin site
admin_site.register(Doctor, DoctorAdmin)
admin_site.register(Staff, StaffAdmin)
admin_site.register(Patient, PatientAdmin)
admin_site.register(Appointment, AppointmentAdmin)
admin_site.register(Record, RecordAdmin)
admin_site.register(User, UserAdmin)
