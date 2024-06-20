from django.shortcuts import render
from rest_framework import generics
from .serializers import GameSerializer
from .models import Game

# all users can see scoreboard data
class ScoreboardView(generics.ListAPIView):
    serializer_class = GameSerializer

    def get_queryset(self):
        return Game.objects.all()