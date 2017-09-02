from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models


# Create your models here.
class UserWrapper(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    key = models.CharField(max_length=40)

    def __str__(self):
        return "User First Name: " + self.user.first_name + ", User Email: " + self.user.email


class Tournament(models.Model):
    login = models.ForeignKey(UserWrapper, on_delete=models.CASCADE)
    matches_per_day = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    number_of_team = models.IntegerField(validators=[MaxValueValidator(50)], default=0)
    number_of_pool = models.IntegerField(default=1)
    type = models.IntegerField()
    available_days = models.IntegerField()
    registration_ending = models.DateField()
    starting_date = models.DateField()
    sport = models.CharField(max_length=30)
    category = models.CharField(max_length=20, default="Open to all")

    def __str__(self):
        return "Tour. ID: " + str(self.id) + ', Type: ' + str(self.type) + ", tour. User: " + str(
            self.login) + ",tour.Category:" + (self.category)


class Pool(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    pool_number = models.IntegerField(default=1)
    number_of_teams = models.IntegerField()


class Point(models.Model):
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE, default=None)
    team = models.CharField(max_length=100)
    wins = models.IntegerField(default=0)

    def __str__(self):
        return self.team + "-" + str(self.wins)


class Match(models.Model):
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE, default=None)
    team1 = models.CharField(max_length=100)
    team2 = models.CharField(max_length=100)
    winner = models.CharField(max_length=1, default='0')

    def __str__(self):
        return str(self.pk) + self.team1 + "V/S" + self.team2 + "->" + self.winner


class GoogleUser(models.Model):
    user_wrapper = models.ForeignKey(UserWrapper)
    google_id = models.CharField(max_length=100)
    image_url = models.CharField(max_length=200)


class FacebookUser(models.Model):
    user_wrapper = models.ForeignKey(UserWrapper)
    fb_id = models.CharField(max_length=100)
    image_url = models.CharField(max_length=200)


class Team(models.Model):
    login = models.ForeignKey(UserWrapper, on_delete=models.CASCADE, blank=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, blank=True)
    team_name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.team_name)


class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    number = models.BigIntegerField()
    email = models.EmailField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str("Team: " + str(self.team) + ", Name of Player: " + self.name)


class SportsSpecification(models.Model):
    no_of_players = models.PositiveIntegerField()
    sport = models.CharField(max_length=50)

    def __str__(self):
        return "No. of players: " + str(self.no_of_players) + ", sport: " + self.sport
