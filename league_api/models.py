from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('coach', 'Coach'),
        ('player', 'Player'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    login_count = models.PositiveIntegerField(default=0)
    total_time_spent = models.DurationField(default='0:00:00')
    email = models.EmailField(unique=True) # Ensure email field is unique

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=255)
    coach = models.OneToOneField(User, on_delete=models.CASCADE, related_name='team')
    average_score = models.FloatField(default=0.0)

class Player(models.Model):
    name = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    height = models.FloatField()
    average_score = models.FloatField(default=0.0)
    games_played = models.PositiveIntegerField(default=0)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')

class Game(models.Model):
    team1 = models.ForeignKey(Team, related_name='team1_games', on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name='team2_games', on_delete=models.CASCADE)
    team1_score = models.PositiveIntegerField()
    team2_score = models.PositiveIntegerField()
    date = models.DateTimeField()
    winner = models.ForeignKey(Team, related_name='wins', on_delete=models.CASCADE,null=True)
    
class LoginActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.email} - {self.login_time}'
    