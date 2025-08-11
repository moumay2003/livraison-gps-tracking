from django.shortcuts import render

# Create your views here.
# frontend/views.py
from django.shortcuts import render

def index(request):
    return render(request, 'frontend/index.html')