from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

# Only logged-in users can view this page
@login_required
def home(request):
    return render(request, 'home.html')

# Processes the login form
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()  # Retrieves the user
            login(request, user)  # Logs the user in
            return redirect('home')  # Redirects to the homepage
    else:
        form = AuthenticationForm()  # Empty form for GET request
    return render(request, 'LoginSysteem/login.html', {'form': form})

# Logs the user out
def logout_view(request):
    logout(request)  
    return redirect('login')  # Redirects to the login page
