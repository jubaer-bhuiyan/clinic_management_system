import json
from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme

from .models import (
    Doctor, Staff, Patient, Appointment, Record, 
    AdminProfile, PendingRecordChange, Message
)
from .forms import AdminProfileForm

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
            # Get or create AdminProfile
            admin_profile, created = AdminProfile.objects.get_or_create(user=user)
            return redirect('admin_profile')
        messages.error(request, 'Invalid admin credentials')
    return render(request, 'main/AdminLogin.html')

@login_required
def admin_profile(request):
    # Get or create AdminProfile
    admin_profile, created = AdminProfile.objects.get_or_create(user=request.user)
    
    doctor_count = Doctor.objects.count()
    staff_count = Staff.objects.count()
    patient_count = Patient.objects.count()
    pending_changes_count = PendingRecordChange.objects.filter(status='pending').count()
    
    context = {
        'admin_profile': admin_profile,
        'doctor_count': doctor_count,
        'staff_count': staff_count,
        'patient_count': patient_count,
        'pending_changes_count': pending_changes_count,
    }
    return render(request, 'main/AdminProfile.html', context)

@login_required
def patient_profile(request):
    if not hasattr(request.user, 'patient'):
        messages.error(request, 'You need to complete your patient profile first.')
        return redirect('patient_registration')
        
    appointments = Appointment.objects.filter(patient=request.user.patient).order_by('-appointment_date', '-appointment_time')
    records = Record.objects.filter(patient=request.user.patient).order_by('-created_at')
    
    # Count upcoming appointments
    upcoming_appointments_count = appointments.filter(
        appointment_date__gte=timezone.now().date(),
        status='PENDING'
    ).count()
    
    # Count completed visits
    completed_visits = appointments.filter(status='COMPLETED').count()
    
    # Count medical records
    medical_records_count = records.count()
    
    # Count unread messages
    unread_messages = Message.objects.filter(
        receiver=request.user,
        read=False
    ).count()
    
    context = {
        'appointments': appointments,
        'records': records,
        'upcoming_appointments_count': upcoming_appointments_count,
        'completed_visits': completed_visits,
        'medical_records_count': medical_records_count,
        'unread_messages': unread_messages,
    }
    return render(request, 'main/PatientProfile.html', context)

@login_required
def edit_profile(request):
    if request.user.is_staff:
        admin_profile, created = AdminProfile.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            form = AdminProfileForm(request.POST, request.FILES, instance=admin_profile, user=request.user)
            if form.is_valid():
                try:
                    form.save(user=request.user)
                    messages.success(request, 'Profile updated successfully')
                    return redirect('admin_profile')
                except Exception as e:
                    messages.error(request, f'Error updating profile: {str(e)}')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
        else:
            form = AdminProfileForm(instance=admin_profile, user=request.user)
        return render(request, 'main/EditProfile.html', {'form': form})
    
    elif hasattr(request.user, 'patient'):
        if request.method == 'POST':
            try:
                user = request.user
                user.first_name = request.POST.get('first_name')
                user.last_name = request.POST.get('last_name')
                user.email = request.POST.get('email')
                user.save()

                patient = user.patient
                patient.phone = request.POST.get('phone')
                patient.address = request.POST.get('address')
                date_of_birth = request.POST.get('date_of_birth')
                if date_of_birth:
                    patient.date_of_birth = date_of_birth
                
                # Handle health information
                blood_type = request.POST.get('blood_type')
                print(f"Received blood type: {blood_type}")  # Debug log
                patient.blood_type = blood_type if blood_type else None
                
                if request.POST.get('height'):
                    patient.height = float(request.POST.get('height'))
                if request.POST.get('weight'):
                    patient.weight = float(request.POST.get('weight'))
                patient.allergies = request.POST.get('allergies')
                
                # Handle profile picture
                profile_picture = request.FILES.get('profile_picture')
                if profile_picture:
                    if patient.profile_picture:
                        patient.profile_picture.delete(save=False)
                    patient.profile_picture = profile_picture
                
                patient.save()
                messages.success(request, 'Profile updated successfully')
                return redirect('patient_profile')
                
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
                print(f"Error in edit_profile: {str(e)}")  # Debug log
        
        # Get the current blood type for debugging
        current_blood_type = request.user.patient.blood_type
        print(f"Current blood type: {current_blood_type}")  # Debug log
        
        return render(request, 'main/EditProfile.html', {
            'user': request.user,
            'blood_types': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        })
    
    elif hasattr(request.user, 'doctor'):
        if request.method == 'POST':
            try:
                user = request.user
                user.first_name = request.POST.get('first_name')
                user.last_name = request.POST.get('last_name')
                user.email = request.POST.get('email')
                user.save()

                doctor = user.doctor
                doctor.specialization = request.POST.get('specialization')
                doctor.phone = request.POST.get('phone')
                doctor.address = request.POST.get('address')
                
                # Handle profile picture
                profile_picture = request.FILES.get('profile_picture')
                if profile_picture:
                    if doctor.profile_picture:
                        doctor.profile_picture.delete(save=False)
                    doctor.profile_picture = profile_picture
                
                doctor.save()
                messages.success(request, 'Profile updated successfully')
                return redirect('doctor_profile')
                
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
        
        return render(request, 'main/EditProfile.html')
    
    elif hasattr(request.user, 'staff'):
        if request.method == 'POST':
            try:
                user = request.user
                user.first_name = request.POST.get('first_name')
                user.last_name = request.POST.get('last_name')
                user.email = request.POST.get('email')
                user.save()

                staff = user.staff
                staff.position = request.POST.get('position')
                staff.phone = request.POST.get('phone')
                staff.address = request.POST.get('address')
                
                # Handle profile picture
                profile_picture = request.FILES.get('profile_picture')
                if profile_picture:
                    if staff.profile_picture:
                        staff.profile_picture.delete(save=False)
                    staff.profile_picture = profile_picture
                
                staff.save()
                messages.success(request, 'Profile updated successfully')
                return redirect('staff_profile')
                
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
        
        return render(request, 'main/EditProfile.html')
    
    messages.error(request, 'Invalid user type')
    return redirect('home')

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
    records = None
    appointments = None
    
    if hasattr(request.user, 'doctor'):
        records = Record.objects.filter(doctor=request.user.doctor).select_related(
            'patient__user', 'doctor__user'
        ).order_by('-created_at')
        appointments = Appointment.objects.filter(
            doctor=request.user.doctor, 
            status='CONFIRMED'
        ).select_related('patient__user')
    elif hasattr(request.user, 'patient'):
        records = Record.objects.filter(patient=request.user.patient).select_related(
            'doctor__user', 'patient__user'
        ).order_by('-created_at')
    elif hasattr(request.user, 'staff') or request.user.is_staff:
        records = Record.objects.all().select_related(
            'doctor__user', 'patient__user'
        ).order_by('-created_at')
        appointments = Appointment.objects.filter(
            status='CONFIRMED'
        ).select_related('patient__user', 'doctor__user')
    
    return render(request, 'main/records.html', {
        'records': records,
        'appointments': appointments
    })

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
            'patient_id': record.patient.id,
            'patient_name': record.patient.user.get_full_name(),
            'doctor_name': record.doctor.user.get_full_name(),
            'date': record.created_at.strftime('%B %d, %Y'),
            'category': record.category,
            'diagnosis': record.diagnosis,
            'prescription': record.prescription,
            'notes': record.notes,
            'status': record.status,
            'patient_health': {
                'blood_type': record.patient.blood_type or 'Not Set',
                'height': f"{record.patient.height or 'Not Set'} cm",
                'weight': f"{record.patient.weight or 'Not Set'} kg",
                'allergies': record.patient.allergies or 'None'
            }
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
        doctor = get_object_or_404(Doctor, id=data.get('doctor'))

        # If user is staff, create pending change
        if hasattr(request.user, 'staff'):
            PendingRecordChange.objects.create(
                staff=request.user.staff,
                change_type='create',
                patient=patient,
                doctor=doctor,
                changes={
                    'category': data.get('category', 'General'),
                    'diagnosis': data.get('diagnosis'),
                    'prescription': data.get('prescription'),
                    'notes': data.get('notes'),
                    'status': data.get('status', 'Active')
                }
            )
            return JsonResponse({
                'success': True,
                'message': 'Record submitted for admin approval'
            })

        # If user is doctor or admin, create record directly
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
        
        # Handle health information
        patient.blood_type = request.POST.get('blood_type')
        if request.POST.get('height'):
            patient.height = float(request.POST.get('height'))
        if request.POST.get('weight'):
            patient.weight = float(request.POST.get('weight'))
        patient.allergies = request.POST.get('allergies')
        
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
        
        # Get health information
        blood_type = request.POST.get('blood_type')
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        allergies = request.POST.get('allergies')
        
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
                address=address,
                blood_type=blood_type,
                height=float(height) if height else None,
                weight=float(weight) if weight else None,
                allergies=allergies
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
    
    # Count upcoming appointments
    upcoming_appointments_count = appointments.filter(
        status='PENDING'
    ).count()
    
    # Count completed visits
    completed_visits = Appointment.objects.filter(
        doctor=request.user.doctor,
        status='COMPLETED'
    ).count()
    
    # Count medical records
    medical_records_count = Record.objects.filter(
        doctor=request.user.doctor
    ).count()
    
    # Count unread messages
    unread_messages = Message.objects.filter(
        receiver=request.user,
        read=False
    ).count()
    
    context = {
        'appointments': appointments,
        'records': records,
        'upcoming_appointments_count': upcoming_appointments_count,
        'completed_visits': completed_visits,
        'medical_records_count': medical_records_count,
        'unread_messages': unread_messages,
    }
    return render(request, 'main/DoctorProfile.html', context)

@login_required
@staff_required
def staff_profile(request):
    today = timezone.now().date()
    
    # Get today's appointments
    today_appointments = Appointment.objects.filter(
        appointment_date=today
    ).select_related('doctor__user', 'patient__user').order_by('appointment_time')
    
    # Get recent records
    recent_records = Record.objects.all().select_related(
        'doctor__user', 'patient__user'
    ).order_by('-created_at')[:10]
    
    # Get statistics
    today_appointments_count = today_appointments.count()
    active_patients = Patient.objects.filter(user__is_active=True).count()
    available_doctors = Doctor.objects.filter(user__is_active=True).count()
    pending_tasks = 0  # This will be implemented when task system is added
    
    context = {
        'today_appointments': today_appointments,
        'recent_records': recent_records,
        'today_appointments_count': today_appointments_count,
        'active_patients': active_patients,
        'available_doctors': available_doctors,
        'pending_tasks': pending_tasks,
        'tasks': [],  # This will be populated when task system is implemented
    }
    return render(request, 'main/StaffProfile.html', context)

@login_required
def add_task(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        
        if not description or not due_date:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Task model will be implemented later
        # For now, just return success
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def update_task(request, task_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        completed = request.POST.get('completed') == 'true'
        
        # Task model will be implemented later
        # For now, just return success
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def delete_task(request, task_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Task model will be implemented later
        # For now, just return success
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def cancel_appointment(request, appointment_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        appointment.status = 'CANCELLED'
        appointment.save()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def check_in_patient(request, appointment_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        if appointment.status != 'CONFIRMED':
            return JsonResponse({'error': 'Appointment must be confirmed first'}, status=400)
        
        appointment.status = 'COMPLETED'
        appointment.save()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def download_record(request, record_id):
    try:
        record = get_object_or_404(Record, id=record_id)
        
        # Generate PDF or other format
        # For now, just return a text response
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="record_{record_id}.txt"'
        
        response.write(f"Patient: {record.patient.user.get_full_name()}\n")
        response.write(f"Doctor: Dr. {record.doctor.user.get_full_name()}\n")
        response.write(f"Date: {record.created_at}\n")
        response.write(f"Category: {record.category}\n")
        response.write(f"Status: {record.status}\n\n")
        
        response.write("Patient Health Information:\n")
        response.write(f"Blood Type: {record.patient.blood_type or 'Not Set'}\n")
        response.write(f"Height: {record.patient.height or 'Not Set'} cm\n")
        response.write(f"Weight: {record.patient.weight or 'Not Set'} kg\n")
        response.write(f"Allergies: {record.patient.allergies or 'None'}\n\n")
        
        response.write(f"Diagnosis:\n{record.diagnosis}\n\n")
        response.write(f"Prescription:\n{record.prescription}\n\n")
        if record.notes:
            response.write(f"Notes:\n{record.notes}\n")
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error downloading record: {str(e)}')
        return redirect('view_record')

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
            # If user is staff, create pending change
            if hasattr(request.user, 'staff'):
                changes = {
                    'category': request.POST.get('category'),
                    'diagnosis': request.POST.get('diagnosis'),
                    'prescription': request.POST.get('prescription'),
                    'notes': request.POST.get('notes'),
                    'status': request.POST.get('status')
                }
                
                PendingRecordChange.objects.create(
                    record=record,
                    staff=request.user.staff,
                    change_type='update',
                    changes=changes
                )
                messages.success(request, 'Record update request submitted for approval.')
                return redirect('view_record')
            
            # If user is doctor or admin, update directly
            record.category = request.POST.get('category')
            record.diagnosis = request.POST.get('diagnosis')
            record.prescription = request.POST.get('prescription')
            record.notes = request.POST.get('notes')
            record.status = request.POST.get('status')
            record.save()
            
            messages.success(request, 'Record updated successfully.')
            return redirect('view_record')
            
        except Exception as e:
            messages.error(request, f'Error updating record: {str(e)}')
    
    return render(request, 'main/EditRecord.html', {'record': record})

@login_required
def check_username(request):
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

@login_required
@admin_required
def pending_changes(request):
    pending_changes = PendingRecordChange.objects.filter(status='pending').select_related(
        'staff__user', 'record', 'patient__user', 'doctor__user'
    )
    return render(request, 'main/PendingChanges.html', {'pending_changes': pending_changes})

@login_required
@admin_required
def approve_change(request, change_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        change = get_object_or_404(PendingRecordChange, id=change_id, status='pending')
        
        if change.change_type == 'create':
            # Create new record
            Record.objects.create(
                patient=change.patient,
                doctor=change.doctor,
                **change.changes
            )
        elif change.change_type == 'update':
            # Update existing record
            for field, value in change.changes.items():
                setattr(change.record, field, value)
            change.record.save()
        elif change.change_type == 'delete':
            # Delete record
            change.record.delete()

        # Update change status
        change.status = 'approved'
        change.admin_notes = request.POST.get('admin_notes', '')
        change.save()

        return JsonResponse({'success': True, 'message': 'Change approved successfully'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@admin_required
def reject_change(request, change_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        change = get_object_or_404(PendingRecordChange, id=change_id, status='pending')
        change.status = 'rejected'
        change.admin_notes = request.POST.get('admin_notes', '')
        change.save()

        return JsonResponse({'success': True, 'message': 'Change rejected successfully'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@admin_required
def get_change_details(request, change_id):
    try:
        change = get_object_or_404(PendingRecordChange, id=change_id)
        
        data = {
            'staff_name': change.staff.user.get_full_name(),
            'created_at': change.created_at.strftime('%B %d, %Y %H:%M'),
            'change_type': change.change_type,
            'changes': change.changes,
        }
        
        if change.change_type == 'create':
            data.update({
                'patient_name': change.patient.user.get_full_name(),
                'doctor_name': change.doctor.user.get_full_name(),
            })
        elif change.change_type == 'update':
            data['original'] = {
                'category': change.record.category,
                'diagnosis': change.record.diagnosis,
                'prescription': change.record.prescription,
                'notes': change.record.notes,
                'status': change.record.status,
            }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def inbox(request):
    messages_received = Message.objects.filter(receiver=request.user).select_related('sender')
    messages_sent = Message.objects.filter(sender=request.user).select_related('receiver')
    unread_count = messages_received.filter(read=False).count()
    
    context = {
        'messages_received': messages_received,
        'messages_sent': messages_sent,
        'unread_count': unread_count,
    }
    return render(request, 'main/inbox.html', context)

@login_required
def compose_message(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver')
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        
        try:
            receiver = User.objects.get(id=receiver_id)
            
            # Check if receiver is a doctor (when sender is patient) or patient (when sender is doctor)
            is_valid = (hasattr(request.user, 'patient') and hasattr(receiver, 'doctor')) or \
                      (hasattr(request.user, 'doctor') and hasattr(receiver, 'patient'))
            
            if not is_valid:
                messages.error(request, 'Invalid recipient. Messages can only be sent between patients and doctors.')
                return redirect('compose_message')
            
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                subject=subject,
                content=content
            )
            messages.success(request, 'Message sent successfully!')
            return redirect('inbox')
            
        except User.DoesNotExist:
            messages.error(request, 'Recipient not found.')
            return redirect('compose_message')
    
    # Get the list of available recipients based on user type
    if hasattr(request.user, 'patient'):
        recipients = User.objects.filter(doctor__isnull=False)
    elif hasattr(request.user, 'doctor'):
        recipients = User.objects.filter(patient__isnull=False)
    else:
        recipients = User.objects.none()
    
    context = {
        'recipients': recipients
    }
    return render(request, 'main/compose_message.html', context)

@login_required
def view_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user has permission to view this message
    if message.sender != request.user and message.receiver != request.user:
        messages.error(request, 'You do not have permission to view this message.')
        return redirect('inbox')
    
    # Mark message as read if the user is the receiver
    if message.receiver == request.user and not message.read:
        message.read = True
        message.save()
    
    context = {
        'message': message
    }
    return render(request, 'main/view_message.html', context)

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user has permission to delete this message
    if message.sender != request.user and message.receiver != request.user:
        messages.error(request, 'You do not have permission to delete this message.')
        return redirect('inbox')
    
    message.delete()
    messages.success(request, 'Message deleted successfully!')
    return redirect('inbox')
