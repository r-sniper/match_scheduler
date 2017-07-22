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

    # def clean(self):
    #     recaptcha_response = self.request.POST.get('g-recaptcha-response')
    #     data = {
    #         'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
    #         'response': recaptcha_response
    #     }
    #     r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    #     result = r.json()
    #     if result['success']:
    #         return True
    #     else:
    #         raise forms.ValidationError('Invalid reCaptcha.')


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


class TournamentForm(forms.ModelForm):
    match_type = forms.ChoiceField(
        choices=[('League Match', 'League Match'), (('Pool Match', 'Pool Match'))])  # , 'Knockout Match'])
    available_hrs = forms.IntegerField(label='Available Hours')
    match_duration = forms.IntegerField()
    break_duration = forms.IntegerField()

    class Meta:
        model = Tournament
        fields = ['available_hrs', 'match_duration', 'break_duration', 'number_of_team', 'number_of_pool',
                  'available_days']
        labels = {
            # 'available_hrs': _('Available hours in a day'),
            'match_duration': _('Match Duration'),
            # 'break_duration': _('Break Duration'),
            'number_of_team': _('Number of Tasdfams'),
            # 'number_of_pool': _('Number of Pools'),
            # 'available_days': _('Available Days')
        }

    # def clean(self):
    #     cleaned_data = super(TournamentForm, self).clean()
    #     hrs = cleaned_data.get('available_hrs')
    #     md = cleaned_data.get('match_duration')
    #     bd = cleaned_data.get('break_duration')
    #
    #     if 0 > hrs or hrs > 24:
    #         msg = 'Available hours should be in between 0 and 24.'
    #         self._errors['available_hrs'] = self.error_class([msg])
    #         del cleaned_data['available_hrs']
    #     if md > hrs:
    #         msg = 'Match duration should be less than available hours.'
    #         self._errors['match_duration'] = self.error_class([msg])
    #         del cleaned_data['match_duration']
    #
    #     if bd > hrs:
    #         msg = 'Break duration should be less than available hours.'
    #         self._errors['break_duration'] = self.error_class([msg])
    #         del cleaned_data['break_duration']
