from django.core.validators import MaxValueValidator
from django.db import models


# Create your models here.

class LoginCredential(models.Model):
    user_name = models.CharField(max_length=20,unique=True)
    password = models.CharField(max_length=50)
    matches_per_day = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    number_of_team = models.IntegerField(validators=[MaxValueValidator(50)])
    def __str__(self):
        return self.user_name


class Point(models.Model):
    login = models.ForeignKey(LoginCredential, on_delete=models.CASCADE)
    team = models.CharField(max_length=100)
    wins = models.IntegerField(default=0)

    def __str__(self):
        return self.team + "-" + str(self.wins)


class Match(models.Model):
    login = models.ForeignKey(LoginCredential, on_delete=models.CASCADE)
    team1 = models.CharField(max_length=100)
    team2 = models.CharField(max_length=100)
    winner = models.CharField(max_length=1, default='0')

    def __str__(self):
        return str(self.pk) + self.team1 + "V/S" + self.team2 + "->" + self.winner
