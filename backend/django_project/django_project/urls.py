"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.middleware.csrf import get_token
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

def signup_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username')
            email = data.get('email')
            password1 = data.get('password1')
            password2 = data.get('password2')

            if password1 != password2:
                return JsonResponse({"error": "Passwords must match"}, status=400)

            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password1)
            return JsonResponse({"message": "User created successfully"}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

def csrf_token_view(request):
    response = JsonResponse({'csrfToken': get_token(request)})
    response.set_cookie('csrftoken', get_token(request), samesite='Lax', secure=False)
    return response

def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({"message": "Login successful"}, status=200)
            else:
                return JsonResponse({"error": "Invalid credentials"}, status=401)
                
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
            
    return JsonResponse({"error": "Invalid request method"}, status=400)

def profile_view(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Unauthorized"}, status=401)
            
        user = request.user
        return JsonResponse({
            "username": user.username,
            "email": user.email,
            "is_authenticated": True,
        }, status=200)  

    return JsonResponse({"error": "Invalid request method"}, status=400)     

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include("allauth.urls")),
    path('csrf/', csrf_token_view, name='csrf_token_view'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('profile/', profile_view, name='profile'),

]
