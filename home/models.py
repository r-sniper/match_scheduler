from django.core.validators import MaxValueValidator
from django.db import models


# Create your models here.

class LoginCredential(models.Model):
    user_name = models.CharField(max_length=20)
    password = models.CharField(max_length=50)
    matches_per_day = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    number_of_team = models.IntegerField(validators=[MaxValueValidator(50)])
    number_of_pool = models.IntegerField(default=1)
    type = models.IntegerField()

    def __str__(self):
        return self.user_name


class Pool(models.Model):
    login = models.ForeignKey(LoginCredential, on_delete=models.CASCADE)
    pool_number = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id) + ' ' + str(self.pool_number)


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
