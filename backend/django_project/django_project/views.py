from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.contrib.auth import logout

from game.models import UserProfile
import json

def profile_view(request):
        if request.method == 'GET':
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Unauthorized"}, status=401)

        user = request.user
        print("profile_view request for user: " + str(user.id))
        print(user.__dict__)
        # Log the session ID
        session_id = request.COOKIES.get('sessionid')
        print("Session ID:", session_id)  # This will print to the console or log file
        profile = user.profile
        win_rate = 0
        if profile.total_games_played > 0:
            win_rate = (profile.total_wins / profile.total_games_played) * 100

        return JsonResponse({
            "username": user.username,
            "email": user.email,
            "total_games_played": profile.total_games_played,
            "total_wins": profile.total_wins,
            "win_rate": round(win_rate, 2),
            "current_streak": profile.current_streak,
            "max_streak": profile.max_streak,
            "average_score": profile.average_score,
            "best_score": profile.best_score,
            "last_played": profile.last_played_date.isoformat() if profile.last_played_date else None,
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
    token = get_token(request)
    print("CSRF token:", token)
    response = JsonResponse({'csrfToken': token})
    response.set_cookie('csrftoken', token, samesite='none', secure=False)
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

def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'Logged out'})

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