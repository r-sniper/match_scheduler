from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models


# Create your models here.
class UserWrapper(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)


class Tournament(models.Model):
    login = models.ForeignKey(UserWrapper, on_delete=models.CASCADE)
    matches_per_day = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    number_of_team = models.IntegerField(validators=[MaxValueValidator(50)])
    number_of_pool = models.IntegerField(default=1)
    type = models.IntegerField()
    available_days = models.IntegerField()

    def __str__(self):
        return str(self.id) + ' ' + str(self.type)


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
