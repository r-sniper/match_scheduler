from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from .models import Tournament


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
        labels = {
            'username': _('User Name'),
            'email': _('E-Mail'),
            'password': _('Password'),
            'first_name': _('First Name'),
            'last_name': _('Last Name')
        }


class TournamentForm(forms.ModelForm):
    match_type = forms.ChoiceField(
        choices=[('League Match', 'League Match'), (('Pool Match', 'Pool Match'))])  # , 'Knockout Match'])
    available_hrs = forms.IntegerField()
    match_duration = forms.IntegerField()
    break_duration = forms.IntegerField()

    class Meta:
        model = Tournament
        fields = ['available_hrs', 'match_duration', 'break_duration', 'number_of_team', 'number_of_pool',
                  'available_days']
        labels = {

            'available_hrs': _('Available hours in a day'),
            'match_duration': _('Match Duration'),
            'break_duration': _('Break Duration'),
            'number_of_team': _('Number of Teams'),
            'number_of_pool': _('Number of Pools'),
            'available_days': _('Available Days')
        }
