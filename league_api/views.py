from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import IntegrityError
from django.utils.timezone import now
from .serializers import GameSerializer, PlayerSerializer, TeamSerializer, RegisterUserSerializer, InitialTeamSerializer
from .models import Game, Team, Player, User
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
    
## Post Calls
# register coach by admin
class RegisterCaochView(APIView):
    serializer_class = RegisterUserSerializer
    def post(self, request, *args, **kwargs):
        try:
            coach = User.objects.create_user(email=request.data['email'], password='coach@123',
                                     username=request.data['username'],
                                     role='coach')
            coach_serializer = self.serializer_class(coach)

        except IntegrityError as e:
            error_message = str(e)
            if 'unique constraint' in error_message:
                if 'email' in error_message:
                    return Response({'detail': 'Email is already in use.'}, status=status.HTTP_400_BAD_REQUEST)
                if 'username' in error_message:
                    return Response({'detail': 'Username is already in use.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'An error occurred.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(coach_serializer.data, status=status.HTTP_201_CREATED)
    
# register players by admin
class RegisterPlayerView(APIView):
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        try:
            player = User.objects.create_user(email=request.data['email'], password='player@123',
                                     username=request.data['username'],
                                     role='player')
            player_serializer = self.serializer_class(player)

        except IntegrityError as e:
            error_message = str(e)
            if 'unique constraint' in error_message:
                if 'email' in error_message:
                    return Response({'detail': 'Email is already in use.'}, status=status.HTTP_400_BAD_REQUEST)
                if 'username' in error_message:
                    return Response({'detail': 'Username is already in use.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'An error occurred.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(player_serializer.data, status=status.HTTP_201_CREATED)

# coach create teams
class CreateTeamView(APIView):
    serializer_class = InitialTeamSerializer

    def post(self, request, *args, **kwargs):
        try:
            team=Team.objects.create(name=request.data['team_name'], coach=request.user)
            team_serializer = self.serializer_class(team)
        except IntegrityError as e:
            error_message = str(e)
            if 'unique constraint' in error_message:
                    return Response({'detail': 'Coach already has a team.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'An error occurred.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(team_serializer.data, status=status.HTTP_201_CREATED)

# players can join team
class JoinTeamView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            team = Team.objects.get(id=request.data['team_id'])

            # Check if the team already has 10 players
            if team.players.count() >= 10:
                return Response({'detail': 'This team already has 10 players.'}, status=status.HTTP_400_BAD_REQUEST)

            Player.objects.create(
                name=request.data['player_name'],
                height=request.data['height'],
                games_played=0,
                average_score=0.0,
                team=team,
                user=request.user  # Linking Player to the User
            )

        except IntegrityError as e:
            error_message = str(e)
            if 'unique constraint' in error_message:
                    return Response({'detail': 'Player already has a team.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'An error occurred.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)

# admin can crete new games
class CreateGameView(APIView):
    serializer_class = GameSerializer

    def post(self, request, *args, **kwargs):
        try:
            team1 = Team.objects.get(id=request.data['team1_id'])
            team2 = Team.objects.get(id=request.data['team2_id'])
            game = Game.objects.create(
                team1=team1,
                team2=team2,
                team1_score=0,
                team2_score=0,
                date=now()
            )
            serializer = self.serializer_class(game)

        except IntegrityError as e:
            return Response({'detail': 'An error occurred.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data,status=status.HTTP_201_CREATED)
    