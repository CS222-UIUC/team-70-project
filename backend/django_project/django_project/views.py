from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils import timezone
#from database_temporary.model import UserProfile
import json

def profile_view(request):
    if request.method == 'GET':
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

@ensure_csrf_cookie
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
# def update_game_stats(request):
#     if request.method == 'POST' and request.user.is_authenticated:
#         try:
#             data = json.loads(request.body)
#             won = data.get('won', False)
#             attempts = data.get('attempts', 0)
            
#             profile, _ = UserProfile.objects.get_or_create(user=request.user)
#             profile.total_games_played += 1
#             if won:
#                 profile.total_wins += 1
#             profile.update_streak(timezone.now().date())
#             profile.save()
            
#             return JsonResponse({'message': 'Stats updated successfully'})
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     return JsonResponse({'error': 'Invalid request'}, status=400)