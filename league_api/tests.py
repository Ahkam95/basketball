from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import User, Team, Player, Game
from django.utils.timezone import now

class CustomAuthTokenViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='admin@basketball.league.com', password='admin@123',
                                             username='admin', role='admin')
        self.create_url = reverse('api_token_auth')
        self.user.refresh_from_db()

    def test_user_success_login(self):
        response = self.client.post(self.create_url, {'username': 'admin', 'password': 'admin@123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_user_fail_login_with_invalid_credential(self):
        response = self.client.post(self.create_url, {'username': 'admin', 'password': '******'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ScoreboardViewTests(APITestCase):
    def setUp(self):
        # Create a user and authenticate
        self.user = User.objects.create_user(email='admin@basketball.league.com',username='admin', password='password123', role='admin')
        self.client.force_authenticate(user=self.user)
        self.coach1 = User.objects.create_superuser(email='coach1@basketball.league.com', password='coach@123',
                                                    username='coach1', role='coach')
        self.coach2 = User.objects.create_superuser(email='coach2@basketball.league.com', password='coach@123',
                                                    username='coach2', role='coach')
        self.team1 = Team.objects.create(name='Team 1', coach=self.coach1)
        self.team2 = Team.objects.create(name='Team 2', coach=self.coach2)

        # Create test game data
        self.game = Game.objects.create(team1=self.team1, team2 = self.team2, team1_score=0, team2_score=0, date=now())

    def test_get_scoreboard(self):
        url = reverse('scoreboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Assuming only one game in the database

class TeamListViewTests(APITestCase):
    def setUp(self):
        # Create a user and authenticate
        self.user = User.objects.create_user(email='admin@basketball.league.com', username='admin', password='password123', role='admin')

        # Create test team data
        self.team = Team.objects.create(name='Team A', coach=self.user)

    def test_get_team_list(self):
        url = reverse('team_list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Assuming only one team in the database

class TeamDetailViewTests(APITestCase):
    def setUp(self):
        # Create a user and authenticate
        self.user = User.objects.create_user( email='coach2@basketball.league.com',username='coach', password='password123', role='coach')

        # Create test team data
        self.team = Team.objects.create(name='Team A', coach=self.user)

    def test_get_team_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('team_detail', kwargs={'pk': self.team.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Team A')

class PlayerListViewTests(APITestCase):
    def setUp(self):
        # Create a user and authenticate
        self.user = User.objects.create_user(email='coach@basketball.league.com',username='coach', password='password123', role='coach')
        self.client.force_authenticate(user=self.user)

        # Create test team data
        self.team = Team.objects.create(name='Team A', coach=self.user)

        self.coach1 = User.objects.create_superuser(email='coach1@basketball.league.com', password='coach@123',
                                                    username='coach1', role='coach')
        self.coach2 = User.objects.create_superuser(email='coach2@basketball.league.com', password='coach@123',
                                                    username='coach2', role='coach')

        # Create test player data
        self.player1 = Player.objects.create(name='Player 1', height=6.1, team=self.team, user=self.coach1)
        self.player2 = Player.objects.create(name='Player 2',height=5.0, team=self.team, user=self.coach2)

    def test_get_player_list(self):
        url = reverse('player_list', kwargs={'pk': self.team.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Assuming two players in the team

class PlayerDetailViewTests(APITestCase):
    def setUp(self):
        # Create a user and authenticate
        self.user = User.objects.create_user(email='coch0@basketball.league.com',username='coach', password='password123', role='coach')


        # Create test team data
        self.team = Team.objects.create(name='Team A', coach=self.user)
        self.coach1 = User.objects.create_superuser(email='coach1@basketball.league.com', password='coach@123',
                                                    username='coach1', role='coach')
        self.coach2 = User.objects.create_superuser(email='coach2@basketball.league.com', password='coach@123',
                                                    username='coach2', role='coach')

        # Create test player data
        self.player = Player.objects.create(name='Player 1', height=6.1, team=self.team, user=self.coach1)


    def test_get_player_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('player_detail', kwargs={'pk': self.player.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Player 1')


class RegisterCoachViewTests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(email='admin@basketball.league.com', password='admin@123',
                                                        username='admin', role='admin')
        self.create_url = reverse('register_coach')
        self.client.force_authenticate(user=self.admin_user)

    def test_register_coach_success(self):
        data = {
            'email': 'coach1@basketball.league.com',
            'username': 'coach1',
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='coach1@basketball.league.com').exists())

    def test_register_coach_fail_duplicate_email(self):
        User.objects.create_user(email='coach1@basketball.league.com', password='coach@123', username='coach1',
                                 role='coach')
        data = {
            'email': 'coach1@basketball.league.com',
            'username': 'coach2',
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Email is already in use.')

    def test_register_coach_fail_duplicate_username(self):
        User.objects.create_user(email='coach2@basketball.league.com', password='coach@123', username='coach1',
                                 role='coach')
        data = {
            'email': 'coach3@basketball.league.com',
            'username': 'coach1',
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Username is already in use.')


class RegisterPlayerViewTests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(email='admin@basketball.league.com', password='admin@123',
                                                        username='admin', role='admin')
        self.create_url = reverse('register_player')
        self.client.force_authenticate(user=self.admin_user)

    def test_register_player_success(self):
        data = {
            'email': 'player1@basketball.league.com',
            'username': 'player1',
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='player1@basketball.league.com').exists())

    def test_register_player_fail_duplicate_email(self):
        User.objects.create_user(email='player1@basketball.league.com', password='player@123', username='player1',
                                 role='player')
        data = {
            'email': 'player1@basketball.league.com',
            'username': 'player2',
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Email is already in use.')

    def test_register_player_fail_duplicate_username(self):
        User.objects.create_user(email='player2@basketball.league.com', password='player@123', username='player1',
                                 role='player')
        data = {
            'email': 'player3@basketball.league.com',
            'username': 'player1',
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Username is already in use.')


class CreateTeamViewTests(APITestCase):

    def setUp(self):
        self.coach_user = User.objects.create_user(email='coach1@basketball.league.com', password='coach@123',
                                                   username='coach1', role='coach')
        self.create_url = reverse('create_team')
        self.client.force_authenticate(user=self.coach_user)

    def test_create_team_success(self):
        data = {
            'team_name': 'Team 1'
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Team.objects.filter(name='Team 1', coach=self.coach_user).exists())

    def test_create_team_fail_duplicate_team(self):
        Team.objects.create(name='Team 1', coach=self.coach_user)
        data = {
            'team_name': 'Team 1'
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Coach already has a team.')


class JoinTeamViewTests(APITestCase):

    def setUp(self):
        self.coach_user = User.objects.create_user(email='coach1@basketball.league.com', password='coach@123',
                                                   username='coach1', role='coach')
        self.team = Team.objects.create(name='Team 1', coach=self.coach_user)
        self.player_user = User.objects.create_user(email='player1@basketball.league.com', password='player@123',
                                                    username='player1', role='player')
        self.join_url = reverse('join_team')
        self.client.force_authenticate(user=self.player_user)

    def test_join_team_success(self):
        data = {
            'player_name': 'John Doe',
            'height': 6.5,
            'team_id': self.team.id,
        }
        response = self.client.post(self.join_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Player.objects.filter(name='John Doe', team=self.team).exists())

    def test_join_team_fail_team_full(self):
        for _ in range(10):
            user = User.objects.create_user(email=f'coach1@basketball{_}.league.com', password='coach@123',
                                     username=f'player_{_}', role='player')
            Player.objects.create(name=f'Player {_}', height=6.0, team=self.team, user= user)

        data = {
            'player_name': 'John Doe',
            'height': 6.5,
            'team_id': self.team.id,
        }
        response = self.client.post(self.join_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'This team already has 10 players.')


class CreateGameViewTests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(email='admin@basketball.league.com', password='admin@123',
                                                        username='admin', role='admin')
        self.coach1 = User.objects.create_superuser(email='coach1@basketball.league.com', password='coach@123',
                                                    username='coach1', role='coach')
        self.coach2 = User.objects.create_superuser(email='coach2@basketball.league.com', password='coach@123',
                                                    username='coach2', role='coach')
        self.team1 = Team.objects.create(name='Team 1', coach=self.coach1)
        self.team2 = Team.objects.create(name='Team 2', coach=self.coach2)
        self.create_url = reverse('create_game')
        self.client.force_authenticate(user=self.admin_user)

    def test_create_game_success(self):
        data = {
            'team1_id': self.team1.id,
            'team2_id': self.team2.id,
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Game.objects.filter(team1=self.team1, team2=self.team2).exists())


class UpdateCountGamesViewTests(APITestCase):

    def setUp(self):
        self.coach_user = User.objects.create_user(email='coach1@basketball.league.com', password='coach@123',
                                                   username='coach1', role='coach')
        self.team = Team.objects.create(name='Team 1', coach=self.coach_user)
        self.player = Player.objects.create(name='Player 1', height=6.0, team=self.team, user=self.coach_user)
        self.update_url = reverse('update_count_played_games')
        self.client.force_authenticate(user=self.coach_user)

    def test_update_count_games_success(self):
        data = {
            'player_id': self.player.id,
        }
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.player.refresh_from_db()
        self.assertEqual(self.player.games_played, 1)


class UpdateTeamScoreViewTests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(email='admin@basketball.league.com', password='admin@123',
                                                        username='admin', role='admin')
        self.coach1 = User.objects.create_superuser(email='coach1@basketball.league.com', password='coach@123',
                                                        username='coach1', role='coach')
        self.coach2 = User.objects.create_superuser(email='coach2@basketball.league.com', password='coach@123',
                                                        username='coach2', role='coach')
        self.team1 = Team.objects.create(name='Team 1', coach=self.coach1)
        self.team2 = Team.objects.create(name='Team 2', coach=self.coach2)
        self.game = Game.objects.create(team1=self.team1, team2=self.team2,team1_score=0, team2_score=0, date=now())

        self.update_url = reverse('update_team_score')
        self.client.force_authenticate(user=self.admin_user)

    def test_update_team_scores_success(self):
        data = {
            'game_id': self.game.id,
            'team1_score': 13,
            'team2_score': ""
        }
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.game.refresh_from_db()
        self.assertEqual(self.game.team1_score, 13)
        self.assertEqual(self.game.team2_score, 0)

class RemovePlayerViewTests(APITestCase):
    def setUp(self):
        # Create a coach user
        self.coach_user = User.objects.create_user(email='coach1@basketball.league.com',username='coach', password='password123', role='coach')

        # Create a player user
        self.player_user = User.objects.create_user(email='player@basketball.league.com',username='player', password='password123', role='player')

        # Create a team with the coach as the coach
        self.team = Team.objects.create(name='Test Team', coach=self.coach_user)

        # Add the player to the team
        self.player = Player.objects.create(name='Player 1',  height=6.0, team=self.team,  user=self.player_user)

        # URL for the RemovePlayerView
        self.url = reverse('remove-player', kwargs={'pk': self.player.id})

    def test_remove_player_by_coach(self):
        self.client.force_authenticate(user=self.coach_user)

        # Make DELETE request to remove the player
        response = self.client.delete(self.url)

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Player.objects.filter(id=self.player.id).exists(), False)

    def test_remove_player_unauthenticated(self):
        # Make DELETE request to remove the player
        response = self.client.delete(self.url)
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Player.objects.filter(id=self.player.id).exists(), True)  # Ensure player still exists

    def test_remove_player_by_non_coach(self):
        self.client.force_authenticate(user=self.player_user)
        # Make DELETE request to remove the player
        response = self.client.delete(self.url)

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Player.objects.filter(id=self.player.id).exists(), True)  # Ensure player still exists


class UpdateAVGTeamScoreViewTests(APITestCase):
    def setUp(self):
        # Create a user and authenticate as admin
        self.user = User.objects.create_user(email='admin@example.com', username='admin', password='password123', role='admin')

        # Create test team data
        self.team = Team.objects.create(name='Team A', coach=self.user)

    def test_update_avg_team_score(self):

        url = reverse('update_avg_team_score')
        self.client.force_authenticate(user=self.user)
        data = {'team_id': self.team.id, 'average_score': 85.5}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.team.refresh_from_db()
        self.assertEqual(self.team.average_score, 85.5)

    def test_update_avg_team_score_invalid_team(self):

        url = reverse('update_avg_team_score')
        self.client.force_authenticate(user=self.user)
        data = {'team_id': 9999, 'average_score': 85.5}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UpdateAVGPlayerScoreViewTests(APITestCase):
    def setUp(self):
        # Create a user and authenticate as admin
        self.user = User.objects.create_user(email='admin@example.com', username='admin', password='password123', role='admin')
        # Create a coach user
        self.coach_user = User.objects.create_user(email='coach1@basketball.league.com', username='coach',
                                                   password='password123', role='coach')

        self.player_user = User.objects.create_user(email='plyer@example.com', username='player', password='password123',
                                             role='player')

        # Create test team and player data
        self.team = Team.objects.create(name='Team A', coach=self.coach_user)
        self.player = Player.objects.create(name='Player 1', team=self.team, height=6.0, user=self.player_user)
        self.player.refresh_from_db()

    def test_update_avg_player_score(self):
        player = Player.objects.get(id=self.player.id)
        url = reverse('update_avg_player_score')
        self.client.force_authenticate(user=self.user)
        data = {'player_id': player.id, 'average_score': 20.0}

        response = self.client.put(url, data )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.player.refresh_from_db()
        self.assertEqual(self.player.average_score, 20.0)

    def test_update_avg_player_score_invalid_player(self):

        url = reverse('update_avg_player_score')
        self.client.force_authenticate(user=self.user)
        data = {'player_id': 9999, 'average_score': 20.0}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)