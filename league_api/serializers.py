from rest_framework import serializers
from .models import User, Team, Player, Game

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'login_count', 'total_time_spent']

class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class WinnerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ['id', 'name']

class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = ['id', 'name', 'height', 'average_score', 'games_played', 'team']

class TeamSerializer(serializers.ModelSerializer):
    coach = UserSerializer()
    players = PlayerSerializer(many=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'coach', 'players','average_score']

class InitialTeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'coach', 'players','average_score']

class GameSerializer(serializers.ModelSerializer):
    team1 = TeamSerializer()
    team2 = TeamSerializer()
    winner = WinnerSerializer()

    class Meta:
        model = Game
        fields = ['id', 'team1', 'team2', 'team1_score', 'team2_score', 'winner', 'date']
