"""
views.py

This module contains the view functions for the API application in the Django project.
It handles the logic for processing requests and returning responses, serving as the
bridge between the models and templates.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
# from rest_framework import status
from allauth.account.decorators import login_required
from django.http import JsonResponse
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
        name = request.GET.get('name', 'Guest')  # Default to 'Guest' if not provided

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
@login_required
@api_view(['GET'])
def get_user_info(request):
    """ 
    get_user_info(request)

    This function responds with user's username and streak given they are logged in
    """
    user = request.user  # Access the authenticated user

    # Prepare user information to return
    user_info = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        # Need to return streak once database is merged
    }

    return JsonResponse(user_info)

@api_view(['GET'])
def get_scrambled_article(request):
    """ 
    get_scrambled_article(request)

    This function responds with serialized, scrambled article data given a user's session token

    request must contain field "token"
    """
    # Iterate through all GET parameters
    get_parameters = {key: request.GET.get(key) for key in request.GET}

    # Prepare the response data
    response_data = {
        "request": "get_scrambled_article",
        "get_parameters": get_parameters,
    }

    return JsonResponse(response_data)

@api_view(['GET'])
def get_guess_scoreboard(request):
    """
    get_guess_scoreboard(request)

    This function response with serialized data on the player's past guesses and their scores

    request must contian field "token"
    """
    # Iterate through all GET parameters
    get_parameters = {key: request.GET.get(key) for key in request.GET}

    # Prepare the response data
    response_data = {
        "request": "get_guess_scoreboard",
        "get_parameters": get_parameters,
        "scores": {
            "test1" : 100,
            "test2" : 200,
        },
    }

    return JsonResponse(response_data)

@api_view(['GET'])
def get_friend_scoreboard(request):
    """
    get_friend_scoreboard(request)

    This function response with serialized data on a players' friends' scores for the day

    request must contian field "token"
    """
    # Iterate through all GET parameters
    get_parameters = {key: request.GET.get(key) for key in request.GET}

    # Prepare the response data
    response_data = {
        "request": "get_friend_scoreboard",
        "get_parameters": get_parameters,
    }

    return JsonResponse(response_data)

@api_view(['POST'])
def process_guess(request):
    """
    process_guess(request)

    This function processes a guess given a user's session token and a guess

    request must contain field "token" and "guess"
    """
    # Iterate through all POST parameters
    get_parameters = {key: request.POST.get(key) for key in request.GET}

    # Prepare the response data
    response_data = {
        "request": "process_guess",
        "get_parameters": get_parameters,
    }

    return Response(response_data)
