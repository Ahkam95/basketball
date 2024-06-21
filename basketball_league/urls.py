from django.contrib import admin
from django.urls import path, include, re_path
from league_api.views import (ScoreboardView, PlayerDetailView, TeamListView, PlayerListView, TeamDetailView, SiteStatisticsView, RegisterCaochView, RegisterPlayerView, CreateGameView, CreateTeamView, CustomAuthToken, LogoutView, CurrentUserView, UpdateCountGamesView, RemovePlayerView, JoinTeamView, UpdateTeamScoreView, UpdateAVGTeamScoreView, UpdateAVGPlayerScoreView)

custom_pool_urls = [

    # API related to authentication
    path('login/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('logout/', LogoutView.as_view(), name='api_token_logout'),
    path('current-user/', CurrentUserView.as_view(), name='get-current-user'),

    # Admin, Coach, Player can be able to access the API
    path('scoreboard/', ScoreboardView.as_view(), name='scoreboard'),
    path('teams/<int:pk>/', TeamDetailView.as_view(), name='team_detail'), # Admin can access all teams, Coach can access only his team details
    path('player/<int:pk>/', PlayerDetailView.as_view(), name='player_detail'),

    # Only for Admin
    path('teams/', TeamListView.as_view(), name='team_list'),
    path('statistics/', SiteStatisticsView.as_view(), name='site_statistics'),
    path('register/coach/', RegisterCaochView.as_view(), name='register_coach'),
    path('register/player/', RegisterPlayerView.as_view(), name='register_player'),
    path('create/game/', CreateGameView.as_view(), name='create_game'),
    path('update-scores-team/', UpdateTeamScoreView.as_view(), name='update_team_score'),
    path('update-avg-scores-team/', UpdateAVGTeamScoreView.as_view(), name='update_avg_team_score'),
    path('update-avg-scores-player/', UpdateAVGPlayerScoreView.as_view(), name='update_avg_player_score'),

    # Only for Coach
    path('teams/<int:pk>/players/', PlayerListView.as_view(), name='player_list'), # Filter avg > 90% players, A coach can see only his team player details.
    path('create/team/', CreateTeamView.as_view(), name='create_team'),
    path('update-count-games/', UpdateCountGamesView.as_view(), name='update_count_played_games'), # A coach can be able to update only his team's player records
    path('players/<int:pk>/remove/', RemovePlayerView.as_view(), name='remove-player'), # A coach can be able to remove only his team's players

    # Only for Player
    path('join/team/', JoinTeamView.as_view(), name='join_team'),
]

urlpatterns = [
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include(custom_pool_urls)),
    path('admin/', admin.site.urls),
]
