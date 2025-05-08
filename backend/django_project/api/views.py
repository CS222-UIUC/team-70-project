"""
views.py

This module contains the view functions for the API application in the Django project.
It handles the logic for processing requests and returning responses, serving as the
bridge between the models and templates.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
# from rest_framework import status
# from allauth.account.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.http import JsonResponse
from . import utils
# IMPORT MODEL FROM DATABASE (IF NEEDED)
# IMPORT SERIALIZER FROM DATABASE OR API (IF NEEDED)


@api_view(['GET', 'POST'])
def example_view(request):
    """
    DEBUG PATH
    """
    # Access the request method
    method = request.method

    # Access GET parameters
    if method == 'GET':
        # Default to 'Guest' if not provided
        name = request.GET.get('name', 'Guest')

    # Access POST parameters
    else:
        name = request.POST.get('name', 'Guest')

    # Access cookies
    user_cookie = request.COOKIES.get('user_id')

    # Access user information
    user = request.user

    # Prepare response data
    response_data = {
        "method": method,
        "name": name,
        "user_cookie": user_cookie,
        "is_authenticated": user.is_authenticated,
        "user_id": user.id if user.is_authenticated else None,
    }

    return Response(response_data)

### API PATHS ###
@api_view(['GET'])
def get_user_info(request):
    """
    get_user_info(request)

    JSON Format:
    user_info = {
        "request": "get_user_info",
        "id" : <user id>,
        "username" : <username>,
        "email" : <email>,
        "streak" : <streak>
    }
    """
    user = request.user  # Access the authenticated user

    print(user)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    print("get_user_info request for user: " + str(user.id))

    # Prepare user information to return
    user_info = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "streak": 0,
        # Need to return streak once database is merged
    }

    return JsonResponse(user_info)

@api_view(['GET'])
def get_scrambled_article(request):
    """
    get_scrambled_article(request)

    This function responds with serialized, scrambled article data given a user's session token

    JSON Format:
    response_data {
        "request": "get_scrambled_article",
        "article": {
            "main-text" : <main text>,
            "header" : <header - optional>,
            "header-text" : <header text - if header>,
            "image-url" : <img url - optional>,
            "image-title" : <img title - if image url>,
            "captions" : {
                "caption1" : <caption 1 - if image url>,
                ...
            }
        }
    }
    """
    user = request.user  # Access the authenticated user

    token = get_token(request)

    print(user)

    print(token)

    # Log the session ID
    session_id = request.COOKIES.get('sessionid')
    print("Session ID Article:", session_id)  # This will print to the console or log file
        

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    print("get_scrambled_article request for user: " + str(user.id))
    
    return JsonResponse(utils.get_user_article(user.id))


@api_view(['GET'])
def get_guess_scoreboard(request):
    """
    get_guess_scoreboard(request)

    This function response with serialized data on the player's past guesses and their scores

    JSON Format:
    response_data = {
        "request" : "get_guess_scoreboard",
        "scores" : {
            <guess1> : <score1>,
            <guess2> : <score2>,
            ...
        }
    }
    """
    user = request.user  # Access the authenticated user

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    print("get_guess_scoreboard request for user: " + str(user.id))

    return JsonResponse(utils.get_user_scores(user.id))


@api_view(['GET'])
def get_friend_scoreboard(request):
    """
    get_friend_scoreboard(request)

    This function response with serialized data on a players' friends' scores for the day

    JSON Format:
    response_data {
        "request": "get_friend_scoreboard",
        "scores" : {
            "friend1" : score1,
            "friend2" : score2,
            ...
        }
    }
    """
    user = request.user  # Access the authenticated user

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    print("get_friend_scoreboard request for user: " + str(user.id))

    # NOT IMPLEMENTED: THIS FEATURE WILL LIKELY BE CUT
    
    # Prepare the response data
    response_data = {
        "request": "get_friend_scoreboard",
        "scores": {}
    }

    return JsonResponse(response_data)


@api_view(['POST'])
def process_guess(request):
    """
    process_guess(request)

    This function processes a guess given a user's session token and a guess

    request must contain field "token" and "guess"
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    # Read guess parameter from post
    guess = request.data.get('guess')
    if guess:
        user = request.user  # Access the authenticated user
        print("Received guess: " + guess + " for user: " + str(user.id))
        utils.process_guess(user.id, guess)
    else:
        print("Unable to parse guess")

    # Prepare the response data
    response_data = {
        "request": "process_guess",
        "guess" : guess
    }

    return Response(response_data)
