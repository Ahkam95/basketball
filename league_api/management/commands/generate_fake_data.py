import random
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from league_api.models import Team, Player, Game

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate fake data for the basketball league'

    def handle(self, *args, **kwargs):
        # Create admin user
        User.objects.create_superuser(email='admin@basketball.league.com', password='admin@123', username='admin',
                                                   role='admin')

        # Create coach users
        coach_users = [User.objects.create_user(email=f'coach{i}@basketball.league.com', password='coach@123', username=f'coach{i}',
                                                role='coach') for i in range(1, 5)]

        # Create teams and assign coaches
        teams = [Team.objects.create(name=f'Team{i}', coach=coach_users[i - 1]) for i in range(1, 5)]

        # Create players and assign to teams
        for team in teams:
            for i in range(10):
                player_name ="player"+str(i)+"_"+str(team.name)
                player_user = User.objects.create_user(
                    email=f'{player_name.lower()}{i}@basketball.league.com',
                    password='player@123',
                    username=f'{player_name.lower()}{i}',
                    role='player'
                )
                Player.objects.create(
                    name=player_name,
                    height=random.uniform(5.5, 7.0),
                    average_score=random.uniform(10.0, 30.0),
                    games_played=random.randint(1, 20),
                    team=team,
                    user=player_user  # Linking Player to the User
                )

        # Create games
        for i in range(1, 11):
            team1, team2 = random.sample(teams, 2)
            Game.objects.create(
                team1=team1,
                team2=team2,
                team1_score=random.randint(50, 100),
                team2_score=random.randint(50, 100),
                date=now(),
                winner=team1 if random.choice([True, False]) else team2
            )

        self.stdout.write(self.style.SUCCESS('Fake data generated successfully'))
