from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Message, Patient, Doctor, Appointment

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
        # For patients, show their assigned doctors from any appointments (including pending)
        assigned_doctors = Doctor.objects.filter(
            appointment__patient__user=request.user,
            appointment__status__in=['PENDING', 'CONFIRMED', 'COMPLETED']
        ).distinct()
        recipients = User.objects.filter(doctor__in=assigned_doctors)
    elif hasattr(request.user, 'doctor'):
        # For doctors, show their patients from any appointments (including pending)
        assigned_patients = Patient.objects.filter(
            appointment__doctor__user=request.user,
            appointment__status__in=['PENDING', 'CONFIRMED', 'COMPLETED']
        ).distinct()
        recipients = User.objects.filter(patient__in=assigned_patients)
    else:
        recipients = User.objects.none()
    
    context = {
        'recipients': recipients,
        'is_patient': hasattr(request.user, 'patient')
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