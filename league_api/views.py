from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.db import IntegrityError
from django.utils.timezone import now
from .serializers import GameSerializer, PlayerSerializer, TeamSerializer, RegisterUserSerializer, InitialTeamSerializer
from .models import Game, Team, Player, User
from .services import get_site_statistics, calculate_90th_percentile, record_logout_and_calculate_time_spent, update_login_count_and_activity
from .permissions import IsAuthenticatedOr401, IsAdmin, IsCoach, IsPlayer


# user login with django auth
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        update_login_count_and_activity(token.user)
        return response

# user logout and past token will be invalid
class LogoutView(APIView):

    permission_classes = [IsAuthenticatedOr401]

    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            record_logout_and_calculate_time_spent(request.user)
            token.delete()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class CurrentUserView(APIView):

    permission_classes = [IsAuthenticatedOr401]

    def get(self, request):
        return Response({"id":request.user.id, "username":request.user.username, "email":request.user.email, "role":request.user.role},status=status.HTTP_200_OK)

# all users can see scoreboard data
class ScoreboardView(generics.ListAPIView):
    
    permission_classes = [IsAuthenticatedOr401]
    serializer_class = GameSerializer

    def get_queryset(self):
        return Game.objects.all()

# get details of given player
class PlayerDetailView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticatedOr401, IsCoach]
    serializer_class = PlayerSerializer

    def get_queryset(self):
        return Player.objects.filter(id=self.kwargs['pk'])
    
# get details of players
class PlayerListView(generics.ListAPIView):

    permission_classes = [IsAuthenticatedOr401, IsCoach]
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

    permission_classes = [IsAuthenticatedOr401, IsAdmin]

    queryset = Team.objects.all()
    serializer_class = TeamSerializer

# get details of given team
class TeamDetailView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticatedOr401, IsCoach]
    serializer_class = TeamSerializer

    def get_queryset(self):
        team = Team.objects.filter(id=self.kwargs['pk'])
        return team

# admin can view details users
class SiteStatisticsView(APIView):

    permission_classes = [IsAuthenticatedOr401, IsAdmin]

    def get(self, request):
        data = get_site_statistics()
        return Response(data)
    
## Post Calls
# register coach by admin
class RegisterCaochView(APIView):

    permission_classes = [IsAuthenticatedOr401, IsAdmin]
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

    permission_classes = [IsAuthenticatedOr401, IsAdmin]
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

    permission_classes = [IsAuthenticatedOr401, IsCoach]
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

    permission_classes = [IsAuthenticatedOr401, IsPlayer]

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

    permission_classes = [IsAuthenticatedOr401, IsAdmin]
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
    
# update the players played matches count
class UpdateCountGamesView(APIView):

    permission_classes = [IsAuthenticatedOr401, IsCoach]
    serializer_class = PlayerSerializer

    def put(self, request, *args, **kwargs):
        try:
            player = Player.objects.get(id=request.data['player_id'])
            player.games_played += 1
            player.save()

            player_serializer = self.serializer_class(player)

        except IntegrityError as e:
            return Response({'detail': 'An error occurred.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(player_serializer.data,status=status.HTTP_200_OK)

# update the team current score
class UpdateTeamScoreView(APIView):

    permission_classes = [IsAuthenticatedOr401, IsAdmin]
    serializer_class = GameSerializer

    def put(self, request, *args, **kwargs):
        try:
            game = Game.objects.get(id=request.data['game_id'])

            if request.data['team1_score']:
                game.team1_score = request.data['team1_score']
            if request.data['team2_score']:
                game.team2_score = request.data['team2_score']

            game.save()
            game_serializer = self.serializer_class(game)

        except IntegrityError as e:
            return Response({'detail': 'An error occurred.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(game_serializer.data,status=status.HTTP_200_OK)

#  update the team average score by admin
class UpdateAVGTeamScoreView(APIView):

    permission_classes = [IsAuthenticatedOr401, IsAdmin]
    serializer_class = TeamSerializer

    def put(self, request, *args, **kwargs):
        try:
            team = Team.objects.get(id=request.data['team_id'])

            if request.data['average_score']:
                team.average_score = request.data['average_score']

            team.save()
            team_serializer = self.serializer_class(team)

        except :
            return Response({'detail': 'An error occurred.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(team_serializer.data,status=status.HTTP_200_OK)

#  update the player average score
class UpdateAVGPlayerScoreView(APIView):

    permission_classes = [IsAuthenticatedOr401, IsAdmin]
    serializer_class = PlayerSerializer

    def put(self, request, *args, **kwargs):
        try:

            player = Player.objects.get(id=request.data['player_id'])

            if request.data['average_score']:
                player.average_score = request.data['average_score']

            player.save()
            player_serializer = self.serializer_class(player)

        except :
            return Response({'detail': 'An error occurred.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(player_serializer.data, status=status.HTTP_200_OK)

#  remove players from team
class RemovePlayerView(APIView):

    permission_classes = [IsAuthenticatedOr401, IsCoach]
    
    def delete(self, request, pk, *args, **kwargs):
        player = get_object_or_404(Player, pk=pk)
        team = player.team

        # Ensure that the requesting user is the coach of the team
        if request.user != team.coach:
            return Response({'detail': 'Only team coach can remove a player'},
                            status=status.HTTP_403_FORBIDDEN)

        player.delete()
        return Response({'detail': 'Player deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
