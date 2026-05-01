from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import PlayerProfile
from .forms import UserLoginForm
from .forms import UserRegistrationForm
from .games import tic_tac_toe
from .games.klondike import Klondike


# --- NEW: Serve the root index.html ---
def index_view(request):
    return render(request, "hello/index.html", {"message": "Welcome to our CS 408 Project!"})


# --- Existing Views ---
def hello_world(request):
    game = None
    if request.user.is_authenticated:
        solitaire = Klondike()
        solitaire.setup_board()
        game = solitaire.to_dict()
    return render(request, "hello/Solitaire.html", {"game": game})


def register_view(request):
    # ... (Keep your existing register code here)
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            PlayerProfile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('hello')
    else:
        form = UserRegistrationForm()
    return render(request, "hello/register.html", {"form": form})


def login_view(request):
    # ... (Keep your existing login code here)
    next_url = request.GET.get('next') or '/'
    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(next_url)
    else:
        form = UserLoginForm()
    return render(request, "hello/login.html", {"form": form})


def tic_tac_toe_view(request):
    return render(request, "hello/tic_tac_toe.html")


def logout_view(request):
    logout(request)  # This destroys the session
    return redirect(request.META.get('HTTP_REFERER', '/'))


def game_directory_view(request):
    return render(request, "hello/game_directory.html")


def statistics_view(request):
    return render(request, "hello/Statistics.html")
