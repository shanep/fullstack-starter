from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone
from datetime import timedelta

# 1. Player Profile (Extends the default Django User for stats)
class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_games_played = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)
    best_score = models.IntegerField(default=0)
    average_completion_time = models.FloatField(default=0.0)  # in seconds
    created_at = models.DateTimeField(auto_now_add=True)

    def win_percentage(self):
        if self.total_games_played == 0:
            return 0
        return round((self.total_wins / self.total_games_played) * 100, 1)

    def update_stats(self):
        """Recalculate stats from all game sessions"""
        sessions = GameSession.objects.filter(player=self.user, is_completed=True)
        self.total_games_played = sessions.count()
        self.total_wins = sessions.filter(is_won=True).count()
        self.total_losses = self.total_games_played - self.total_wins
        self.best_score = sessions.aggregate(models.Max('score'))['score__max'] or 0
        
        completed_sessions = sessions.filter(time_elapsed__isnull=False)
        if completed_sessions.exists():
            avg_time = completed_sessions.aggregate(models.Avg('time_elapsed'))['time_elapsed__avg']
            self.average_completion_time = avg_time or 0.0
        
        self.save()

    def __str__(self):
        return f"{self.user.username}'s Profile"

# 2. Game Variant (Keeps track of Polymorphic games like Klondike vs Spider)
class GameVariant(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    name = models.CharField(max_length=50, unique=True)  # e.g., "Klondike", "Spider", "FreeCell"
    description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    deck_count = models.IntegerField(default=1)  # 1 or 2 decks
    rules = models.TextField(blank=True)

    def __str__(self):
        return self.name

# 3. Game Session (Records individual game history and states)
class GameSession(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    game_variant = models.ForeignKey(GameVariant, on_delete=models.CASCADE)
    
    # Timing and Status
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_won = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)  # True if game ended (won or lost)
    is_abandoned = models.BooleanField(default=False)  # True if player quit
    score = models.IntegerField(default=0)
    moves_count = models.IntegerField(default=0)
    time_elapsed = models.FloatField(null=True, blank=True)  # in seconds
    
    # This will let you save the exact state of the cards if they leave midway!
    game_state = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """Calculate time_elapsed when game ends"""
        if self.is_completed and not self.time_elapsed and self.end_time:
            delta = self.end_time - self.start_time
            self.time_elapsed = delta.total_seconds()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.player.username} - {self.game_variant.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

# 4. Game Statistics (Aggregate stats per player per variant)
class GameStatistic(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    game_variant = models.ForeignKey(GameVariant, on_delete=models.CASCADE)
    total_played = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    win_percentage = models.FloatField(default=0.0)
    average_time = models.FloatField(default=0.0)  # in seconds
    best_score = models.IntegerField(default=0)
    worst_score = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('player', 'game_variant')
        verbose_name_plural = "Game Statistics"

    def update_from_sessions(self):
        """Recalculate stats from completed sessions"""
        sessions = GameSession.objects.filter(
            player=self.player,
            game_variant=self.game_variant,
            is_completed=True
        )
        self.total_played = sessions.count()
        self.total_wins = sessions.filter(is_won=True).count()
        self.win_percentage = (self.total_wins / self.total_played * 100) if self.total_played > 0 else 0
        
        completed_with_time = sessions.filter(time_elapsed__isnull=False)
        if completed_with_time.exists():
            self.average_time = completed_with_time.aggregate(models.Avg('time_elapsed'))['time_elapsed__avg'] or 0
            self.best_score = completed_with_time.aggregate(models.Max('score'))['score__max'] or 0
            self.worst_score = completed_with_time.aggregate(models.Min('score'))['score__min'] or 0
        
        self.save()

    def __str__(self):
        return f"{self.player.username} - {self.game_variant.name}"