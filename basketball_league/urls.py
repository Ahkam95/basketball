from django.contrib import admin
from django.urls import path, include
from league_api.views import (ScoreboardView, PlayerDetailView, TeamListView, PlayerListView, TeamDetailView, SiteStatisticsView, RegisterCaochView, RegisterPlayerView, CreateGameView, CreateTeamView)

custom_pool_urls = [
    path('scoreboard/', ScoreboardView.as_view(), name='scoreboard'),
    path('player/<int:pk>/', PlayerDetailView.as_view(), name='player_detail'),
    path('teams/<int:pk>/players/', PlayerListView.as_view(), name='player_list'),
    path('teams/', TeamListView.as_view(), name='team_list'),
    path('teams/<int:pk>/', TeamDetailView.as_view(), name='team_detail'),
    path('statistics/', SiteStatisticsView.as_view(), name='site_statistics'),

    path('register/coach/', RegisterCaochView.as_view(), name='register_coach'),
    path('register/player/', RegisterPlayerView.as_view(), name='register_player'),
    path('create/game/', CreateGameView.as_view(), name='create_game'),
    path('create/team/', CreateTeamView.as_view(), name='create_team'),
]

urlpatterns = [
    path('', include(custom_pool_urls)),
    path('admin/', admin.site.urls),
]
