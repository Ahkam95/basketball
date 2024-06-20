from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import IntegrityError
from .serializers import GameSerializer, PlayerSerializer, TeamSerializer
from .models import Game, Team, Player
from .services import get_site_statistics, calculate_90th_percentile

# all users can see scoreboard data
class ScoreboardView(generics.ListAPIView):
    serializer_class = GameSerializer
    def get_queryset(self):
        return Game.objects.all()

# get details of given player
class PlayerDetailView(generics.RetrieveAPIView):
    serializer_class = PlayerSerializer
    def get_queryset(self):
        return Player.objects.filter(id=self.kwargs['pk'])
    
# get details of players
class PlayerListView(generics.ListAPIView):
    serializer_class = PlayerSerializer
    def get_queryset(self):
        # team = Team.objects.get(id=self.kwargs['pk'])
        team = get_object_or_404(Team, id=self.kwargs['pk'])
        is_percentile_90 = self.request.query_params.get('is_percentile_90', 'False')
        print(is_percentile_90)
        players = team.players.all()

        if is_percentile_90 == 'False':
            return players

        # Collect individual average scores of all players in the team
        average_scores = list(players.values_list('average_score', flat=True))
        if average_scores:
            # Calculate the 90th percentile score
            percentile_90 = calculate_90th_percentile(average_scores)

            # Filter players whose average score is in the 90th percentile
            filtered_players = players.filter(average_score__gte=percentile_90)
            return filtered_players
        else:
            return players.none()

# get list of team
class TeamListView(generics.ListAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

# get details of given team
class TeamDetailView(generics.RetrieveAPIView):
    serializer_class = TeamSerializer
    def get_queryset(self):
        team = Team.objects.filter(id=self.kwargs['pk'])
        return team

# admin can view details users
class SiteStatisticsView(APIView):
    def get(self, request):
        data = get_site_statistics()
        return Response(data)
    