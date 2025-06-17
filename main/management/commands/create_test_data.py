from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Doctor, Patient, Record
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Creates test data for the CAMS system'

    def handle(self, *args, **kwargs):
        # Create test doctor if not exists
        if not User.objects.filter(username='testdoctor').exists():
            doctor_user = User.objects.create_user(
                username='testdoctor',
                password='testpass123',
                first_name='John',
                last_name='Doe',
                email='doctor@example.com'
            )
            doctor = Doctor.objects.create(
                user=doctor_user,
                specialization='General Medicine',
                phone='1234567890',
                address='123 Medical Center'
            )
            self.stdout.write(self.style.SUCCESS('Created test doctor'))

        # Create test patient if not exists
        if not User.objects.filter(username='testpatient').exists():
            patient_user = User.objects.create_user(
                username='testpatient',
                password='testpass123',
                first_name='Jane',
                last_name='Smith',
                email='patient@example.com'
            )
            patient = Patient.objects.create(
                user=patient_user,
                phone='0987654321',
                address='456 Patient Street',
                date_of_birth='1990-01-01'
            )
            self.stdout.write(self.style.SUCCESS('Created test patient'))

        # Get or create the doctor and patient
        doctor = Doctor.objects.get(user__username='testdoctor')
        patient = Patient.objects.get(user__username='testpatient')

        # Create test records
        categories = ['General', 'Emergency', 'Follow-up', 'Specialist']
        statuses = ['Active', 'Completed', 'Follow-up Required']
        diagnoses = [
            'Common Cold',
            'Seasonal Allergies',
            'Hypertension',
            'Diabetes Check',
            'Annual Physical'
        ]
        prescriptions = [
            'Rest and fluids',
            'Antihistamines',
            'Blood pressure medication',
            'Insulin management',
            'Vitamins and supplements'
        ]

        # Create 10 records with different dates
        for i in range(10):
            Record.objects.create(
                patient=patient,
                doctor=doctor,
                category=random.choice(categories),
                diagnosis=random.choice(diagnoses),
                prescription=random.choice(prescriptions),
                notes=f'Test notes for record {i+1}',
                status=random.choice(statuses),
                created_at=timezone.now() - timedelta(days=random.randint(0, 30))
            )
            self.stdout.write(self.style.SUCCESS(f'Created test record {i+1}'))

        self.stdout.write(self.style.SUCCESS('Successfully created all test data')) 