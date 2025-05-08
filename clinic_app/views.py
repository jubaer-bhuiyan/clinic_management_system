from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def patientreg(request):
    return render(request, 'patientregistration.html')

def availdoc(request):
    return render(request, 'availabledoctors.html')

def aboutus(request):
    return render(request, 'aboutus.html')

def userlogin(request):
    return render(request, 'userlogin.html')

def adminlogin(request):
    return render(request, 'adminlogin.html')