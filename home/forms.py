import requests
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from .models import Tournament, Team, Player#, SportSpecification


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

    # def clean(self):
        # recaptcha_response = self.data.get('g-recaptcha-response')
        # data = {
        #     'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        #     'response': recaptcha_response
        # }
        # r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        # result = r.json()
        # if not result['success']:
        #     msg = 'Invalid reCaptcha.'
        #     self._errors['available_hrs'] = self.error_class([msg])
        #     raise forms.ValidationError('Invalid reCaptcha.')

    def clean_email(self):
        # Get the email
        email = self.cleaned_data.get('email')

        # Check to see if any users already exist with this email as a username.
        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            # Unable to find a user, this is fine
            return email

        # A user was found with this as a username, raise an error.
        raise forms.ValidationError('This email address is already in use.')

sport_dict = []
class TournamentForm(forms.ModelForm):
    match_type = forms.ChoiceField(
        choices=[('League Match', 'League Match'), (('Pool Match', 'Pool Match'))])  # , 'Knockout Match'])
    # available_hrs = forms.IntegerField(label='Available Hours')
    av_hr = forms.IntegerField(label='Available Hours')
    av_min = forms.IntegerField(label='Available Minutes')
    match_hr = forms.IntegerField(label='Match Hours')
    match_min = forms.IntegerField(label='Match Minutes')
    break_hr = forms.IntegerField(label='Break Hours')
    break_min = forms.IntegerField(label='Break Minutes')

    # for i in SportSpecification.objects.all().values_list('sport', flat=True):
    #     sport_dict.append(i)
    sport = forms.ChoiceField(choices=[(i,sport_dict[i]) for i in range(len(sport_dict))])
    widgets = {
        'starting_date': forms.DateInput(attrs={'class': 'datepicker'}),
        'registration_ending': forms.DateInput(attrs={'class': 'datepicker'})
    }

    class Meta:
        model = Tournament
        fields = ['av_hr', 'av_min', 'match_hr', 'match_min', 'break_hr', 'break_min', 'number_of_pool',
                  'available_days', 'sport', 'starting_date', 'registration_ending']
        labels = {
            # 'available_hrs': _('Available hours in a day'),
            'match_duration': _('Match Duration'),
            # 'break_duration': _('Break Duration'),
            'number_of_team': _('Number of Tasdfams'),
            # 'number_of_pool': _('Number of Pools'),
            # 'available_days': _('Available Days')
        }

    def clean(self):
        cleaned_data = super(TournamentForm, self).clean()
        av_hr = cleaned_data.get('av_hr')
        av_min = cleaned_data.get('av_min')
        match_hr = cleaned_data.get('match_hr')
        match_min = cleaned_data.get('match_min')
        break_hr = cleaned_data.get('break_hr')
        break_min = cleaned_data.get('break_min')
        md = cleaned_data.get('match_duration')
        bd = cleaned_data.get('break_duration')

        hrs = av_hr + av_min / 60
        md = match_hr + match_min / 60
        bd = break_hr + break_min / 60

        if 0 > hrs or hrs > 24:
            msg = 'Available hours should be in between 0 and 24.'
            self._errors['available_hrs'] = self.error_class([msg])
            del cleaned_data['available_hrs']
        if md > hrs:
            msg = 'Match duration should be less than available hours.'
            self._errors['match_duration'] = self.error_class([msg])
            del cleaned_data['match_duration']

        if bd > hrs:
            msg = 'Break duration should be less than available hours.'
            self._errors['break_duration'] = self.error_class([msg])
            del cleaned_data['break_duration']


class TeamForm(forms.ModelForm):
    # tournament = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    # login = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))

    class Meta:
        model = Team
        fields = '__all__'
        exclude = ('login',)


class PlayerForm(forms.ModelForm):
    # number = forms.IntegerField(widget=forms.NumberInput(attrs={'min': '999999999',
    #                                                            'max': '9999999999'}))
    class Meta:
        model = Player
        fields = '__all__'
