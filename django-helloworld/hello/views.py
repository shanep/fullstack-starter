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


# --- NEW: Serve the root index.html ---
def index_view(request):
    return render(request, "hello/index.html", {"message": "Welcome to our CS 408 Project!"})


# --- Game Directory View ---
def game_directory_view(request):
    """Display all available game variants"""
    variants = GameVariant.objects.all().order_by('name')
    context = {'variants': variants}
    return render(request, "hello/game_directory.html", context)


# --- Game View (Dynamic based on variant) ---
@login_required(login_url='login')
def play_game(request, variant_name):
    """Play a specific game variant"""
    try:
        variant = GameVariant.objects.get(name__iexact=variant_name)
    except GameVariant.DoesNotExist:
        return redirect('game_directory')
    
    game = None
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
    
    # Create game session record
    session = GameSession.objects.create(
        player=request.user,
        game_variant=variant
    )
    
    context = {
        'game': game,
        'variant': variant,
        'session_id': session.id
    }
    return render(request, "hello/game.html", context)


# --- Existing Views ---
def hello_world(request):
    """Redirect to game directory or show default game"""
    if request.user.is_authenticated:
        return redirect('game_directory')
    return render(request, "hello/hello_world.html")


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
    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('hello')
    else:
        form = UserLoginForm()
    return render(request, "hello/login.html", {"form": form})


def tic_tac_toe_view(request):
    return render(request, "hello/tic_tac_toe.html")


def logout_view(request):
    logout(request)  # This destroys the session
    return redirect('index')


# --- Statistics & Leaderboard Views ---
@login_required(login_url='login')
def statistics_view(request):
    """Display player statistics and leaderboard"""
    player_profile = PlayerProfile.objects.get(user=request.user)
    player_profile.update_stats()
    
    # Player's stats by variant
    user_stats = GameStatistic.objects.filter(player=request.user)
    
    # Global leaderboard
    leaderboard = PlayerProfile.objects.all().order_by('-total_wins')[:10]
    
    context = {
        'player_profile': player_profile,
        'user_stats': user_stats,
        'leaderboard': leaderboard,
    }
    return render(request, "hello/statistics.html", context)


@login_required(login_url='login')
def game_history_view(request):
    """Display player's game history"""
    variant = request.GET.get('variant', None)
    
    query = GameSession.objects.filter(
        player=request.user,
        is_completed=True
    ).order_by('-end_time')
    
    if variant:
        query = query.filter(game_variant__name__iexact=variant)
    
    games = query[:50]  # Limit to 50 most recent games
    variants = GameVariant.objects.all()
    
    context = {
        'games': games,
        'variants': variants,
        'selected_variant': variant,
    }
    return render(request, "hello/game_history.html", context)


# --- AJAX Endpoints for Game Result Recording ---
@login_required(login_url='login')
@require_POST
def save_game_result(request):
    """AJAX endpoint to save game result"""
    import json
    
    data = json.loads(request.body)
    session_id = data.get('session_id')
    is_won = data.get('is_won', False)
    score = data.get('score', 0)
    moves = data.get('moves', 0)
    
    try:
        session = GameSession.objects.get(id=session_id, player=request.user)
        session.end_time = timezone.now()
        session.is_won = is_won
        session.score = score
        session.moves_count = moves
        session.is_completed = True
        session.save()
        
        # Update player profile
        profile = PlayerProfile.objects.get(user=request.user)
        profile.update_stats()
        
        # Update game statistics
        stat, created = GameStatistic.objects.get_or_create(
            player=request.user,
            game_variant=session.game_variant
        )
        stat.update_from_sessions()
        
        return JsonResponse({'status': 'success'})
    except GameSession.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Session not found'}, status=404)
