from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Doctor, Staff, Patient, AdminProfile

class DoctorAdminForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(widget=forms.PasswordInput, required=False)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    class Meta:
        model = Doctor
        fields = ['specialization', 'phone', 'address']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

class StaffAdminForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(widget=forms.PasswordInput, required=False)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    class Meta:
        model = Staff
        fields = ['position', 'phone', 'address']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

class PatientAdminForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(widget=forms.PasswordInput, required=False)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    class Meta:
        model = Patient
        fields = ['phone', 'address', 'date_of_birth']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

class AdminProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = AdminProfile
        fields = ['phone', 'address', 'profile_picture']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            if profile_picture.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError("Image file too large ( > 5MB )")
            if not profile_picture.content_type.startswith('image/'):
                raise forms.ValidationError("File type not supported")
        return profile_picture

    def save(self, user=None, commit=True):
        profile = super().save(commit=False)
        if user:
            profile.user = user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            if commit:
                user.save()
        if commit:
            profile.save()
        return profile 