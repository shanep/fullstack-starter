from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import PlayerProfile, GameVariant, GameSession, GameStatistic
from .forms import UserLoginForm
from .forms import UserRegistrationForm
from .games import tic_tac_toe
from .games.klondike import Klondike
from .games.spider import Spider
from .games.freecell import FreeCell
from datetime import timedelta

# --- Root Project View ---
def index_view(request):
    return render(request, "hello/index.html", {"message": "Welcome to our CS 408 Project!"})

# --- Game Directory View ---
def game_directory_view(request):
    """Display all available games (Solitaire, Tic-Tac-Toe, etc.)"""
    variants = GameVariant.objects.all().order_by('name')
    context = {'variants': variants}
    return render(request, "hello/game_directory.html", context)

# --- Solitaire Landing Page / Hub ---
def hello_world(request):
    """
    Main landing page for Solitaire. 
    Authenticated users see the variant selector (Hub).
    Unauthenticated users see the marketing landing page.
    """
    # Logic removed: We no longer redirect authenticated users away.
    # They stay here to choose Klondike, Spider, or FreeCell.
    return render(request, "hello/hello_world.html")

# --- Game View (Dynamic based on variant) ---
@login_required(login_url='login')
def play_game(request, variant_name):
    """Starts a session and renders the solitaire board for a specific variant"""
    try:
        variant = GameVariant.objects.get(name__iexact=variant_name)
    except GameVariant.DoesNotExist:
        variant = GameVariant.objects.create(name=variant_name.capitalize())
    
    if variant_name.lower() == 'klondike':
        game_obj = Klondike()
    elif variant_name.lower() == 'spider':
        game_obj = Spider()
    elif variant_name.lower() == 'freecell':
        game_obj = FreeCell()
    else:
        return redirect('game_directory')
    
    game_obj.setup_board()
    game = game_obj.to_dict()
    
    session = GameSession.objects.create(
        player=request.user,
        game_variant=variant
    )
    
    context = {
        'game': game,
        'variant': variant,
        'session_id': session.id
    }
    
    return render(request, "hello/Solitaire.html", context)

# --- Auth Routes ---
def register_view(request):
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
    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('hello')
    else:
        form = UserLoginForm()
    return render(request, "hello/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect('index')

# --- Legacy/Other Games ---
def tic_tac_toe_view(request):
    return render(request, "hello/tic_tac_toe.html")

# --- Statistics and History ---
@login_required(login_url='login')
def statistics_view(request):
    player_profile = PlayerProfile.objects.get(user=request.user)
    player_profile.update_stats()
    
    user_stats = GameStatistic.objects.filter(player=request.user)
    leaderboard = PlayerProfile.objects.all().order_by('-total_wins')[:10]
    
    context = {
        'player_profile': player_profile,
        'user_stats': user_stats,
        'leaderboard': leaderboard,
    }
    return render(request, "hello/statistics.html", context)

@login_required(login_url='login')
def game_history_view(request):
    variant = request.GET.get('variant', None)
    query = GameSession.objects.filter(player=request.user, is_completed=True).order_by('-end_time')
    
    if variant:
        query = query.filter(game_variant__name__iexact=variant)
    
    context = {
        'games': query[:50],
        'variants': GameVariant.objects.all(),
        'selected_variant': variant,
    }
    return render(request, "hello/game_history.html", context)

# --- API Endpoints ---
@login_required(login_url='login')
@require_POST
def save_game_result(request):
    import json
    data = json.loads(request.body)
    session_id = data.get('session_id')
    
    try:
        session = GameSession.objects.get(id=session_id, player=request.user)
        session.end_time = timezone.now()
        session.is_won = data.get('is_won', False)
        session.score = data.get('score', 0)
        session.moves_count = data.get('moves', 0)
        session.is_completed = True
        session.save()
        
        profile = PlayerProfile.objects.get(user=request.user)
        profile.update_stats()
        
        stat, _ = GameStatistic.objects.get_or_create(player=request.user, game_variant=session.game_variant)
        stat.update_from_sessions()
        
        return JsonResponse({'status': 'success'})
    except GameSession.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Session not found'}, status=404)