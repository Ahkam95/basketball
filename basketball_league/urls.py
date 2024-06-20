from django.contrib import admin
from django.urls import path, include
from league_api.views import (ScoreboardView)


custom_pool_urls = [
    path('scoreboard/', ScoreboardView.as_view(), name='scoreboard'),
]

urlpatterns = [
    path('', include(custom_pool_urls)),
    path('admin/', admin.site.urls),
]
