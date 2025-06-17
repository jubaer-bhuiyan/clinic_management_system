from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Doctor, Staff, Patient, Appointment, Record
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from functools import wraps
from django.utils import timezone
from django.http import JsonResponse
import json
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.http import url_has_allowed_host_and_scheme

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'You must be an admin to access this page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def doctor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'doctor'):
            messages.error(request, 'You must be a doctor to access this page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'staff'):
            messages.error(request, 'You must be a staff member to access this page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def home(request):
    return render(request, 'main/Home.html')

def about_us(request):
    return render(request, 'main/AboutUs.html')

def user_login(request):
    # Get next URL from either GET or POST
    next_url = request.POST.get('next', request.GET.get('next', ''))
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to next URL if provided and safe
            if next_url:
                if url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
                    return redirect(next_url)
            # Otherwise redirect to appropriate dashboard
            if hasattr(user, 'doctor'):
                return redirect('doctor_profile')
            elif hasattr(user, 'staff'):
                return redirect('staff_profile')
            else:
                return redirect('patient_profile')
        messages.error(request, 'Invalid username or password')
    return render(request, 'main/UserLogin.html', {'next': next_url})

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_profile')
        messages.error(request, 'Invalid admin credentials')
    return render(request, 'main/AdminLogin.html')

@login_required
def admin_profile(request):
    return render(request, 'main/AdminProfile.html')

@login_required
def patient_profile(request):
    if not hasattr(request.user, 'patient'):
        messages.error(request, 'You need to complete your patient profile first.')
        return redirect('patient_registration')
        
    appointments = Appointment.objects.filter(patient=request.user.patient).order_by('-appointment_date', '-appointment_time')
    records = Record.objects.filter(patient=request.user.patient).order_by('-created_at')
    
    context = {
        'appointments': appointments,
        'records': records,
    }
    return render(request, 'main/PatientProfile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        if hasattr(user, 'patient'):
            patient = user.patient
            patient.phone = request.POST.get('phone')
            patient.address = request.POST.get('address')
            patient.date_of_birth = request.POST.get('date_of_birth')
            patient.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('patient_profile')
        elif hasattr(user, 'doctor'):
            doctor = user.doctor
            doctor.phone = request.POST.get('phone')
            doctor.address = request.POST.get('address')
            doctor.specialization = request.POST.get('specialization')
            doctor.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('doctor_profile')
        elif hasattr(user, 'staff'):
            staff = user.staff
            staff.phone = request.POST.get('phone')
            staff.address = request.POST.get('address')
            staff.position = request.POST.get('position')
            staff.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('staff_profile')
    
    return render(request, 'main/EditProfile.html')

@login_required
def take_appointment(request):
    if not hasattr(request.user, 'patient'):
        messages.error(request, 'You need to complete your patient profile first.')
        return redirect('patient_registration')

    selected_doctor_id = request.GET.get('doctor_id')
    doctors = Doctor.objects.select_related('user').all()
    selected_doctor = None
    today = timezone.now().date()
    
    if selected_doctor_id:
        try:
            selected_doctor = Doctor.objects.get(id=selected_doctor_id)
        except Doctor.DoesNotExist:
            messages.error(request, 'Selected doctor not found.')
            return redirect('available_doctors')
    
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')
        
        if not all([doctor_id, appointment_date, appointment_time, reason]):
            messages.error(request, 'Please fill all required fields.')
            return render(request, 'main/TakeAppointment.html', {
                'doctors': doctors,
                'selected_doctor': selected_doctor,
                'today': today
            })
        
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            
            # Check if appointment already exists
            existing_appointment = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time
            ).exists()
            
            if existing_appointment:
                messages.error(request, 'This time slot is already booked. Please choose another time.')
                return render(request, 'main/TakeAppointment.html', {
                    'doctors': doctors,
                    'selected_doctor': selected_doctor,
                    'today': today
                })
            
            Appointment.objects.create(
                patient=request.user.patient,
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                reason=reason,
                status='PENDING'
            )
            messages.success(request, 'Appointment scheduled successfully')
            return redirect('patient_profile')
            
        except Doctor.DoesNotExist:
            messages.error(request, 'Invalid doctor selection.')
    
    return render(request, 'main/TakeAppointment.html', {
        'doctors': doctors,
        'selected_doctor': selected_doctor,
        'today': today
    })

def available_doctors(request):
    doctors = Doctor.objects.select_related('user').all()
    return render(request, 'main/AvailableDoctors.html', {'doctors': doctors})

@login_required
@admin_required
def view_doctors(request):
    doctors = Doctor.objects.select_related('user').all()
    return render(request, 'main/ViewDoctors.html', {'doctors': doctors})

@login_required
@admin_required
def view_staffs(request):
    staffs = Staff.objects.select_related('user').all()
    return render(request, 'main/ViewStaffs.html', {'staffs': staffs})

@login_required
@admin_required
def add_doctor(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        specialization = request.POST.get('specialization')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        try:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return render(request, 'main/AddDoctor.html')
                
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            Doctor.objects.create(
                user=user,
                specialization=specialization,
                phone=phone,
                address=address
            )
            
            messages.success(request, 'Doctor added successfully')
            return redirect('view_doctors')
            
        except Exception as e:
            messages.error(request, f'Error adding doctor: {str(e)}')
            
    return render(request, 'main/AddDoctor.html')

@login_required
@admin_required
def edit_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    if request.method == 'POST':
        user = doctor.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        
        if request.POST.get('password'):
            user.set_password(request.POST.get('password'))
        
        user.save()
        
        doctor.specialization = request.POST.get('specialization')
        doctor.phone = request.POST.get('phone')
        doctor.address = request.POST.get('address')
        doctor.save()
        
        messages.success(request, 'Doctor updated successfully')
        return redirect('view_doctors')
        
    return render(request, 'main/EditDoctor.html', {'doctor': doctor})

@login_required
@admin_required
def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    user = doctor.user
    user.delete()  # This will also delete the doctor due to CASCADE
    messages.success(request, 'Doctor deleted successfully')
    return redirect('view_doctors')

@login_required
@admin_required
def add_staff(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        position = request.POST.get('position')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        try:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return render(request, 'main/AddStaff.html')
                
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            Staff.objects.create(
                user=user,
                position=position,
                phone=phone,
                address=address
            )
            
            messages.success(request, 'Staff member added successfully')
            return redirect('view_staffs')
            
        except Exception as e:
            messages.error(request, f'Error adding staff: {str(e)}')
            
    return render(request, 'main/AddStaff.html')

@login_required
@admin_required
def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    
    if request.method == 'POST':
        user = staff.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        
        if request.POST.get('password'):
            user.set_password(request.POST.get('password'))
        
        user.save()
        
        staff.position = request.POST.get('position')
        staff.phone = request.POST.get('phone')
        staff.address = request.POST.get('address')
        staff.save()
        
        messages.success(request, 'Staff member updated successfully')
        return redirect('view_staffs')
        
    return render(request, 'main/EditStaff.html', {'staff': staff})

@login_required
@admin_required
def delete_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    user = staff.user
    user.delete()  # This will also delete the staff due to CASCADE
    messages.success(request, 'Staff member deleted successfully')
    return redirect('view_staffs')

@login_required
@admin_required
def manage_patient_profile(request):
    patients = Patient.objects.select_related('user').all()
    return render(request, 'main/ManagePatientProfile.html', {'patients': patients})

@login_required
def view_record(request):
    # Initialize records based on user role
    if hasattr(request.user, 'patient'):
        records = Record.objects.filter(patient=request.user.patient)
    elif hasattr(request.user, 'doctor'):
        records = Record.objects.filter(doctor=request.user.doctor)
    elif hasattr(request.user, 'staff') or request.user.is_staff:
        records = Record.objects.all()
    else:
        messages.error(request, 'Unauthorized access')
        return redirect('login')

    records = records.select_related('patient__user', 'doctor__user').order_by('-created_at')

    # Get filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    doctor_id = request.GET.get('doctor')
    category = request.GET.get('category')
    status = request.GET.get('status')
    search = request.GET.get('search')

    # Apply search filter
    if search:
        records = records.filter(
            Q(patient__user__first_name__icontains=search) |
            Q(patient__user__last_name__icontains=search) |
            Q(doctor__user__first_name__icontains=search) |
            Q(doctor__user__last_name__icontains=search) |
            Q(diagnosis__icontains=search) |
            Q(prescription__icontains=search) |
            Q(notes__icontains=search)
        )

    # Apply date filters
    if date_from:
        records = records.filter(created_at__date__gte=date_from)
    if date_to:
        records = records.filter(created_at__date__lte=date_to)

    # Apply doctor filter
    if doctor_id:
        records = records.filter(doctor_id=doctor_id)

    # Apply category filter
    if category:
        records = records.filter(category=category)

    # Apply status filter
    if status:
        records = records.filter(status=status)

    # Get all doctors for the filter dropdown
    doctors = Doctor.objects.select_related('user').all()

    context = {
        'records': records,
        'doctors': doctors,
        'categories': Record.CATEGORY_CHOICES,
        'statuses': Record.STATUS_CHOICES
    }
    return render(request, 'main/Record.html', context)

@login_required
@require_http_methods(["GET"])
def get_record_details(request, record_id):
    if not (hasattr(request.user, 'doctor') or hasattr(request.user, 'staff') or request.user.is_staff or hasattr(request.user, 'patient')):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        record = Record.objects.select_related('doctor__user', 'patient__user').get(id=record_id)
        
        # Check if user has permission to view this record
        if hasattr(request.user, 'patient') and record.patient.user != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        elif hasattr(request.user, 'doctor') and record.doctor.user != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        data = {
            'patient_name': record.patient.user.get_full_name(),
            'doctor_name': record.doctor.user.get_full_name(),
            'date': record.created_at.strftime('%B %d, %Y'),
            'category': record.category,
            'diagnosis': record.diagnosis,
            'prescription': record.prescription,
            'notes': record.notes,
            'status': record.status
        }
        return JsonResponse(data)
    except Record.DoesNotExist:
        return JsonResponse({'error': 'Record not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def add_record(request):
    if not (hasattr(request.user, 'doctor') or hasattr(request.user, 'staff') or request.user.is_staff):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        data = json.loads(request.body)
        patient = get_object_or_404(Patient, id=data.get('patient'))
        
        # If user is a doctor, use their profile
        if hasattr(request.user, 'doctor'):
            doctor = request.user.doctor
        else:
            doctor = get_object_or_404(Doctor, id=data.get('doctor'))

        record = Record.objects.create(
            patient=patient,
            doctor=doctor,
            category=data.get('category', 'General'),
            diagnosis=data.get('diagnosis'),
            prescription=data.get('prescription'),
            notes=data.get('notes'),
            status=data.get('status', 'Active')
        )

        return JsonResponse({
            'success': True,
            'message': 'Record added successfully',
            'record_id': record.id
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def update_record(request, record_id):
    if not (hasattr(request.user, 'doctor') or hasattr(request.user, 'staff') or request.user.is_staff):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        record = get_object_or_404(Record, id=record_id)
        data = json.loads(request.body)

        # Only allow doctors to update their own records
        if hasattr(request.user, 'doctor') and record.doctor.user != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        # Update fields
        record.category = data.get('category', record.category)
        record.diagnosis = data.get('diagnosis', record.diagnosis)
        record.prescription = data.get('prescription', record.prescription)
        record.notes = data.get('notes', record.notes)
        record.status = data.get('status', record.status)
        record.save()

        return JsonResponse({
            'success': True,
            'message': 'Record updated successfully'
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'main/ChangePassword.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
@admin_required
def edit_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        user = patient.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        
        if request.POST.get('password'):
            user.set_password(request.POST.get('password'))
        
        user.save()
        
        patient.phone = request.POST.get('phone')
        patient.address = request.POST.get('address')
        patient.date_of_birth = request.POST.get('date_of_birth')
        patient.save()
        
        messages.success(request, 'Patient updated successfully')
        return redirect('manage_patient_profile')
        
    return render(request, 'main/EditPatient.html', {'patient': patient})

@login_required
@admin_required
def delete_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    user = patient.user
    user.delete()  # This will also delete the patient due to CASCADE
    messages.success(request, 'Patient deleted successfully')
    return redirect('manage_patient_profile')

@login_required
@admin_required
def view_patient_records(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    records = Record.objects.filter(patient=patient).select_related('doctor__user')
    return render(request, 'main/PatientRecords.html', {
        'patient': patient,
        'records': records
    })

def patient_registration(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        date_of_birth = request.POST.get('date_of_birth')
        address = request.POST.get('address')
        
        # Validate username
        if not username or len(username) < 3:
            messages.error(request, 'Username must be at least 3 characters long')
            return redirect('patient_registration')
            
        if not username.isalnum() and '_' not in username:
            messages.error(request, 'Username can only contain letters, numbers, and underscores')
            return redirect('patient_registration')
            
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Username is already taken')
            return redirect('patient_registration')
        
        try:
            # Create user account
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create patient profile
            patient = Patient.objects.create(
                user=user,
                phone=phone,
                date_of_birth=date_of_birth,
                address=address
            )
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('user_login')
            
        except Exception as e:
            messages.error(request, 'An error occurred during registration. Please try again.')
            if user:
                user.delete()
            return redirect('patient_registration')
    
    return render(request, 'main/PatientRegistration.html')

def doctor_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and hasattr(user, 'doctor'):
            login(request, user)
            return redirect('doctor_profile')
        messages.error(request, 'Invalid doctor credentials')
    return render(request, 'main/DoctorLogin.html')

def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and hasattr(user, 'staff'):
            login(request, user)
            return redirect('staff_profile')
        messages.error(request, 'Invalid staff credentials')
    return render(request, 'main/StaffLogin.html')

@login_required
@doctor_required
def doctor_profile(request):
    # Get upcoming appointments
    appointments = Appointment.objects.filter(
        doctor=request.user.doctor,
        appointment_date__gte=timezone.now().date()
    ).select_related('patient__user').order_by('appointment_date', 'appointment_time')
    
    # Get recent records
    records = Record.objects.filter(
        doctor=request.user.doctor
    ).select_related('patient__user').order_by('-created_at')[:10]  # Get only the 10 most recent records
    
    context = {
        'appointments': appointments,
        'records': records,
    }
    return render(request, 'main/DoctorProfile.html', context)

@login_required
@staff_required
def staff_profile(request):
    today = timezone.now().date()
    today_appointments = Appointment.objects.filter(
        appointment_date=today
    ).order_by('appointment_time')
    
    recent_records = Record.objects.all().order_by('-created_at')[:10]
    
    context = {
        'today_appointments': today_appointments,
        'recent_records': recent_records,
    }
    return render(request, 'main/StaffProfile.html', context)

@login_required
@require_http_methods(["POST"])
def update_appointment_status(request, appointment_id):
    if not (hasattr(request.user, 'doctor') or hasattr(request.user, 'staff') or request.user.is_staff):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        data = json.loads(request.body)
        status = data.get('status')

        if status not in ['CONFIRMED', 'CANCELLED', 'COMPLETED']:
            return JsonResponse({'error': 'Invalid status'}, status=400)

        # Only allow doctors to update their own appointments
        if hasattr(request.user, 'doctor') and appointment.doctor.user != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        appointment.status = status
        appointment.save()

        return JsonResponse({
            'success': True,
            'message': f'Appointment status updated to {status}'
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def edit_record(request, record_id):
    record = get_object_or_404(Record, id=record_id)
    
    # Check permissions
    if not (hasattr(request.user, 'doctor') or hasattr(request.user, 'staff') or request.user.is_staff):
        messages.error(request, 'You do not have permission to edit records.')
        return redirect('view_record')
        
    # Only allow doctors to edit their own records
    if hasattr(request.user, 'doctor') and record.doctor.user != request.user:
        messages.error(request, 'You can only edit your own records.')
        return redirect('view_record')
    
    if request.method == 'POST':
        try:
            # Update record fields
            record.category = request.POST.get('category', record.category)
            record.diagnosis = request.POST.get('diagnosis', record.diagnosis)
            record.prescription = request.POST.get('prescription', record.prescription)
            record.notes = request.POST.get('notes', record.notes)
            record.status = request.POST.get('status', record.status)
            record.save()
            
            messages.success(request, 'Record updated successfully')
            return redirect('view_record')
            
        except Exception as e:
            messages.error(request, f'Error updating record: {str(e)}')
    
    context = {
        'record': record,
        'categories': Record.CATEGORY_CHOICES,
        'statuses': Record.STATUS_CHOICES
    }
    return render(request, 'main/EditRecord.html', context)

def check_username(request):
    """
    Check if a username is available.
    Returns JSON response with availability status.
    """
    username = request.GET.get('username', '').strip()
    
    if not username:
        return JsonResponse({'available': False, 'message': 'Username is required'})
    
    # Check if username meets basic requirements
    if len(username) < 3:
        return JsonResponse({'available': False, 'message': 'Username must be at least 3 characters long'})
    
    if not username.isalnum() and '_' not in username:
        return JsonResponse({'available': False, 'message': 'Username can only contain letters, numbers, and underscores'})
    
    # Check if username exists
    exists = User.objects.filter(username__iexact=username).exists()
    
    return JsonResponse({
        'available': not exists,
        'message': 'Username is available' if not exists else 'Username is already taken'
    })
