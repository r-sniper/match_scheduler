import datetime
import hashlib
import json
import logging
import math
import random
import urllib
import facebook
import nexmo
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.utils.crypto import get_random_string

from home.conf import email_sending_service_enabled
from . import conf
from .forms import TournamentForm, UserForm, TeamForm, PlayerForm
from .models import Tournament, Point, UserWrapper, GoogleUser, Team, Player, Pool, Match, SportsSpecification, \
    FacebookUser
import datetime
logger = logging.getLogger(__name__)


def user_logged_in(request):
    user_id = request.session.get('user_id', 0)
    if not user_id:
        return 0
    else:
        return user_id


# Add a tournament
def get_information(request):
    user_id = user_logged_in(request)
    form = TournamentForm()
    # If user exists then he can add tournament

    if user_id:
        if request.method == "POST":
            user_obj = User.objects.get(pk=user_id)
            print(user_obj.userwrapper.key)
            if user_obj.userwrapper.key == 'verified':

                form = TournamentForm(request.POST)
                if form.is_valid():

                    user_wrapper = user_obj.userwrapper

                    logger.debug(user_wrapper.user.username)
                    type_of_match = form.cleaned_data.get('match_type')
                    avalaible_hrs = form.cleaned_data.get("av_hr") + (form.cleaned_data.get("av_min")) / 60
                    match_duration = form.cleaned_data.get("match_hr") + (form.cleaned_data.get('match_min')) / 60
                    break_duration = form.cleaned_data.get("break_hr") + (form.cleaned_data.get('break_min')) / 60

                    # count = int(request.POST.get("category_counter"))
                    entered_category = request.POST.getlist('category')
                    print('Categories:', entered_category)
                    logger.debug(request.POST)
                    logger.debug("entered_category:       ", entered_category)
                    all_tournaments = []

                    for i in entered_category:
                        tournament = form.save(commit=False)
                        # tournament.login = user_wrapper
                        # tournament.matches_per_day = (int)(avalaible_hrs / (match_duration + break_duration))
                        # logger.debug("mathes per day" + str(tournament.matches_per_day))
                        # tournament.sport = form.cleaned_data.get('sport')
                        # print("asdfghjklasdfghj" + tournament.sport, form.cleaned_data.get('sport'))
                        type = 1
                        if type_of_match == 'Pool Match':
                            type = 2

                        all_tournaments.append(Tournament(login=user_wrapper, matches_per_day=(int)(
                            avalaible_hrs / (match_duration + break_duration)),
                                                          number_of_team=tournament.number_of_team,
                                                          number_of_pool=tournament.number_of_pool, type=type,
                                                          available_days=tournament.available_days,
                                                          registration_ending=tournament.registration_ending,
                                                          starting_date=tournament.starting_date,
                                                          sport=form.cleaned_data.get('sport'), category=i))

                    print("All:", all_tournaments)

                    Tournament.objects.bulk_create(all_tournaments)

                    # **********************
                    # for i in range(count):
                    #     all_categories.append(
                    #         Category(type=request.POST.get('category' + str(i + 1)), tournament=tournament))
                    # Category.objects.bulk_create(all_categories)
                    # ************************
                    # group1 = []
                    # group2 = []
                    # list1 = []
                    # list2 = []
                    # user_name = user_obj.username

                    # number_of_teams = tournament.number_of_team
                    # number_of_days = tournament.available_days
                    # matches_per_day = tournament.matches_per_day
                    # number_of_pool = tournament.number_of_pool
                    # Our conventions
                    # 1. League matches
                    # 2. Pool System
                    # 3. Knockout

                    # League matches


                    # category.save()
                    print("scheduling")
                    # logger.debug(type)

                    # logger.debug(Pool.objects.filter(login=user_wrapper))
                    # logger.debug(user_wrapper.pool_set.all()   )
                    return HttpResponseRedirect('/dashboard/')
                else:
                    logger.debug("else " + str(form.errors))

            else:
                return render(request, 'home/information.html', {
                    'form': form,
                    'logged_in': True,
                    'error': conf.email_verification_error
                })

        else:
            form = TournamentForm()
            logger.debug('not post in get_information')
        return render(request, 'home/information.html', {
            'form': form,
            'logged_in': True
        })
    else:
        return render(request, 'home/home_page.html', {
            'logged_in': False
        })


def dashboard(request):
    # print(request.user)
    # if str(request.user) == 'AnonymousUser':
    #     return render(request, 'home/register.html', {'form': UserForm, 'info': 'Please Log in First.'})

    user_id = user_logged_in(request)
    logger.debug('dashboard', request.session.get('user', 0))
    if user_id:
        user = User.objects.get(pk=user_id)
        user_wrapper = user.userwrapper
        hosted_tournament = user_wrapper.tournament_set.all()
        number_of_pool = 0
        participated = user_wrapper.team_set.all()
        if hosted_tournament:
            print(hosted_tournament)
            print("Tournament exists")
        print(participated)
        return render(request, 'home/dashboard.html', {
            'logged_in': True,
            'hosted_tournament': hosted_tournament,
            'participated': participated
        })
    else:
        return render(request, 'home/register.html', {
            'logged_in': False,
            'form': UserForm,
            'info': 'Please Log in First.'
        })


def register(request, context={'goto': '/dashboard/'}):
    goto = '/dashboard/'
    logger.debug('register function', request.method, 'context=', context, context.get('goto'), 'request = ', request)
    user_id = request.session.get('user_id', 0)
    if request.method == "POST" and request.POST.get('submit', 0):
        print("register")
        form = UserForm(data=request.POST)
        print(form.errors)
        if form.is_valid():
            new_user = form.save()
            new_user.set_password(new_user.password)
            new_user.save()
            new_user_wrapper = UserWrapper(user=new_user)
            print(new_user.email)
            new_user_wrapper.key = generate_activation_key()
            link = conf.site_initial_link + '/verification/email/' + new_user_wrapper.key + \
                   '/' + new_user.username
            if email_sending_service_enabled:
                send_mail('SpoFit Email Verification',
                          link,
                          'akzarma2@gmail.com',
                          [new_user.email], fail_silently=False)

            new_user_wrapper.save()
            request.session.set_expiry(10 * 60)
            request.session['user_id'] = new_user.id
            # logger.debug('reference = ', ref)
            logger.debug(User.objects.get(pk=new_user.pk).first_name)
            if request.POST.get('goto', 0):
                goto = request.POST.get('goto')
            return HttpResponseRedirect(goto)
        else:
            logger.debug("Form was not valid because of" + str(form.errors))
    else:
        if user_id:
            return HttpResponseRedirect(goto)
        form = UserForm()
        context['form'] = form
        # context['ref'] = ref
        logger.debug(context)

    return render(request, 'home/register.html', context)


def generate_activation_key():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    secret_key = get_random_string(20, chars)

    return hashlib.sha256((secret_key).encode('utf-8')).hexdigest()


# Works perfectly(Do not touch)
# Convention for pool_number
# 0- To show all available for this tuornament
# 1- To show 1st pool
# 2- To show 2nd pool
# n- to show nth pool
def schedule(request, tournament_number, pool_number=1):
    pool_number = int(pool_number)
    tournament_number = int(tournament_number)
    # For when winner is selected
    if request.is_ajax():
        logger.debug('HeLlO')
        text = request.POST.get('winner_name').split(':')
        match_id = text[1]
        winner = text[0]
        user_id = request.session['user_id']
        user_obj = User.objects.get(id=user_id)
        user_wrapper = user_obj.userwrapper
        logger.debug(winner)
        logger.debug(user_id)
        # if not needed(will review it later)
        if request.is_ajax:
            tournament = user_wrapper.tournament_set.all()
            current_tournament = tournament[tournament_number]
            logger.debug('pool number' + str(pool_number))
            pool_obj = current_tournament.pool_set.get(pool_number=pool_number)
            match_obj_rows = pool_obj.match_set.all()
            match_obj = match_obj_rows.get(id=match_id)
            if match_obj.winner == '0':
                point_obj = Point.objects.get(pool=pool_obj, team=winner)
                point_obj.wins += 2
                point_obj.save()
            elif match_obj.winner == '1' and match_obj.team2 == winner:
                point_obj = Point.objects.get(pool=pool_obj, team=match_obj.team1)
                point_obj.wins -= 2
                point_obj.save()
                point_obj = Point.objects.get(pool=pool_obj, team=winner)
                point_obj.wins += 2
                point_obj.save()
            elif match_obj.winner == '2' and match_obj.team1 == winner:
                point_obj = Point.objects.get(pool=pool_obj, team=match_obj.team2)
                point_obj.wins -= 2
                point_obj.save()
                point_obj = Point.objects.get(pool=pool_obj, team=winner)
                point_obj.wins += 2
                point_obj.save()
            if match_obj.team1 == winner:
                match_obj.winner = '1'
            else:
                match_obj.winner = '2'
            logger.debug('Saving now')
            match_obj.save()
            return HttpResponse("Yipeee done(AJAX)" + str(match_id) + str(winner))
        else:
            return HttpResponse("Not Ajax")
    # For when a pool is selected
    elif request.method == 'POST':

        if request.POST.get('Pool'):
            pool_number = request.POST.get('Pool')
            return HttpResponseRedirect('/schedule/' + str(tournament_number) + '/' + str(pool_number))

        else:
            return HttpResponse("Something went wrong")
    else:
        # logger.debug("submit")
        type = 0
        user_id = user_logged_in(request)
        if not user_id:
            return HttpResponseRedirect('/')
        user_obj = User.objects.get(id=user_id)
        user_wrapper = user_obj.userwrapper
        tournament_obj = user_wrapper.tournament_set.all()
        logger.debug(tournament_obj)
        logger.debug('tournament' + str(tournament_number))
        logger.debug('pool' + str(pool_number))

        user_name = user_obj.username
        current_tournament = tournament_obj[tournament_number]
        number_of_pool = current_tournament.number_of_pool
        number_of_teams = current_tournament.number_of_team
        pool_obj = current_tournament.pool_set.all()

        # show schedule for that pool
        if number_of_pool == 1 or pool_number:
            if pool_number == 0:
                logger.debug("pool number was zero")
                logger.debug("Setting it ot one")
                pool_number = 1
            current_pool = pool_obj[pool_number - 1]

            number_of_teams = current_pool.number_of_teams
            matches_per_day = current_tournament.matches_per_day
            team_per_pool = number_of_teams
            number_of_matches = (team_per_pool * (team_per_pool - 1) / 2)
            minimum_days = int(math.ceil(number_of_matches / matches_per_day))
            match_obj_rows = current_pool.match_set
            match_id_list = match_obj_rows.values_list('id', flat=True)
            list1 = list(match_obj_rows.values_list('team1', flat=True))
            list2 = list(match_obj_rows.values_list('team2', flat=True))
            logger.debug(list1)
            print("Schedule:Minimum Days", minimum_days, "numberofmatches", number_of_matches)
            logger.debug(number_of_teams)
            return render(request, 'home/schedule.html/',
                          {
                              'number_of_days': range(minimum_days),
                              'matches_per_day_list': range(matches_per_day), 'list1': list1, 'list2': list2,
                              'match_id': match_id_list,
                              'matches_per_day': matches_per_day, 'user_name': user_name, 'user_id': user_id,
                              'number_of_pool': number_of_pool,
                              'pool_number': pool_number,
                              'tournament_number': tournament_number,
                              'logged_in': True,
                              'pool_id': current_pool.id
                          })
        # Show all pools
        else:
            rows = int(math.floor(number_of_pool / 2))
            logger.debug("Number of teams(Points table):" + str(number_of_teams))
            logger.debug("Number of pool(Points table):" + str(number_of_pool))
            logger.debug("Number of teams(Points table):" + str(pool_obj[0].number_of_teams))
            team_per_pool = int(number_of_teams / number_of_pool)
            all_teams = []
            for pool in pool_obj:
                all_teams += pool.point_set.values_list('team', flat=True)
            logger.debug(all_teams)
            extra = 0
            if number_of_pool % 2 == 1:
                extra = number_of_pool - 1
            return render(request, 'home/pool.html', {
                'rows': range(rows),
                'max': team_per_pool,
                'all_teams': all_teams,
                'team_per_pool': range(team_per_pool),
                'extra': extra,
                'tournament_number': tournament_number,
                'logged_in': True,
                'pool_id': pool_obj.pk
            })


#
# return HttpResponse(
#     "Something seriously went wrong."
#     "Please mail at 'rshahshah2890@gmail.com when you get this error,"
#     "also explain the situation when you got this error'")


def test_send_email(request):
    message = 'This is a test message from rahul shah.Please reply if got.'
    subject = 'Rahul Shah (Test mail from Django)'
    from_email = settings.EMAIL_HOST
    to_email = [
        from_email,
        'siddheshkand123@gmail.com'
    ]
    # 'raunak3434@gmail.com',
    # 'omkarsarkate22@gmail.com',
    # 'shibashismallik@gmail.com',

    if email_sending_service_enabled:
        send_mail(subject, message, from_email, to_email, fail_silently=False)

    return HttpResponse("Successfully sent")


def resend_mail(request):
    user_id = request.session.get('user_id', 0)
    error = ''
    print(user_id)
    if user_id:
        user = User.objects.get(pk=user_id)
        link = conf.site_initial_link + '/verification/email/' + user.userwrapper.key + \
               '/' + user.username
        if email_sending_service_enabled:
            send_mail('SpoFit Email Verification',
                      link,
                      'siddheshkand123@gmail.com',
                      [user.email], fail_silently=False)
            success = 'Successfully Sent.'
        else:
            error = 'Mail not Sent.'
    return dashboard(request)


# Basic home page(information about spofit)
def home_page(request):
    goto = '/dashboard/'
    logger.debug(request.method)
    # logger.debug(request.session.get_expiry_age())

    if request.method == "POST":

        user_name = request.POST.get('uname')
        password = request.POST.get('pass')
        user = authenticate(username=user_name, password=password)

        if user is not None:

            user_obj = User.objects.get(username=user)
            request.session.set_expiry(10 * 60)
            request.session['user_id'] = user_obj.id
            if request.POST.get('goto', 0):
                goto = request.POST.get('goto')
            return HttpResponseRedirect(goto)

        else:
            return render(request, 'home/register.html', {'form': UserForm()})

    else:
        logger.debug(request.session.get_expiry_age())
        user_id = user_logged_in(request)
        logger.debug(request.session.get_expiry_age())
        if not user_id:
            return render(request, "home/home_page.html", {
                'logged_in': False

            })
        else:
            return render(request, 'home/dashboard.html', {
                'logged_in': True
            })


def points_table(request, tournament_number, pool_number):
    pool_number = int(pool_number)
    tournament_number = int(tournament_number)
    user_id = user_logged_in(request)

    if user_id:
        user_obj = User.objects.get(pk=user_id)
        # logger.debug(user_id)
        user_wrapper = user_obj.userwrapper
        tournament_obj = user_wrapper.tournament_set.all()
        current_tournament = tournament_obj[tournament_number]
        pool_obj = current_tournament.pool_set.get(pool_number=pool_number)
        logger.debug("Hello")
        logger.debug(pool_obj.pool_number)
        number_of_pool = current_tournament.number_of_pool
        full_table = pool_obj.point_set.order_by('-wins').all
        logger.debug(full_table)
        return render(request, 'home/points_table.html', {
            'full_table': full_table,
            'pool_number': pool_number,
            'logged_in': True,
            'number_of_pool': number_of_pool,
            'tournament_number': tournament_number
        })
    else:
        return render(request, 'home/home_page.html', {
            'logged_in': False
        })


def logout(request):
    if request.POST.get('logout'):
        request.session.flush()
        return HttpResponseRedirect('/')


def round_robin(all_teams):
    number_of_teams = len(all_teams)
    odd = False
    if number_of_teams % 2 == 1:
        odd = True
        number_of_teams += 1
        all_teams += ['dummy']
    group1 = []
    group2 = []
    list1 = []
    list2 = []
    for i in range(int(number_of_teams / 2)):
        group1 += [all_teams[i]]
        group2 += [all_teams[i + int(number_of_teams / 2)]]

    for i in range(number_of_teams - 1):
        list1.extend(group1)
        list2.extend(group2)
        group1.insert(1, group2[0])
        group2.remove(group2[0])
        group2.append(group1[int(number_of_teams / 2)])
        group1.remove(group1[int(number_of_teams / 2)])

    if odd:
        index = list1.index('dummy')
        while index:
            list1.pop(index)
            list2.pop(index)
            try:
                index = list1.index('dummy')
            except:
                break

        index = list2.index('dummy')
        while index:
            list1.pop(index)
            list2.pop(index)
            try:
                index = list2.index('dummy')
            except:
                break
    list3 = list(zip(list1, list2))
    # logger.debug(list3)
    return list3


def google_sign_in(request):
    if request.is_ajax:
        print("Got google data")
        id = request.POST.get('id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        image = request.POST.get('image')
        logger.debug(id, email, image, name)
        # Use doesn't exists just set session
        user = User.objects.filter(email=email).first()
        if not user:
            logger.debug('user doesnt exist')
            user = User(username=id, first_name=name, email=email)
            user.save()
            user_wrapper = UserWrapper(user=user)
            user_wrapper.key = 'verified'
            user_wrapper.save()
            google_user = GoogleUser(google_id=id, user_wrapper=user_wrapper, image_url=image)
            google_user.save()
        request.session.set_expiry(10 * 60)
        request.session['user_id'] = user.id
        return HttpResponse("/dashboard/")
    else:
        print("should never go here")


def view_all_tournament(request, error=''):
    # logger.debug(Tournament.objects.all()[1].category_set.values_list('type', flat=True))
    return render(request, 'home/view_tournaments.html', {
        'all_tournaments': Tournament.objects.all(),
        'error': error,
    })


def register_team(request):
    tournament_id = -1
    user = user_logged_in(request)
    logger.debug("Method123:" + str(request))
    print('Registration Tournament')
    # return HttpResponse("Here")
    if user:
        user_obj = User.objects.get(pk=user)
        print(user_obj.userwrapper)
        if user_obj.userwrapper.key == 'verified':
            logger.debug(request)
            if request.POST.get('tournament_id', 0):
                tournament_id = request.POST.get('tournament_id')
                logger.debug(tournament_id)
            tournament = get_object_or_404(Tournament, pk=tournament_id)

            user_wrapper = user_obj.userwrapper
            team = Team(login=user_wrapper, tournament=tournament)

            if request.POST.get('register_team', 0):
                team_form = TeamForm(request.POST)
                if team_form.is_valid():
                    exists = tournament.team_set.filter(team_name=team_form.cleaned_data['team_name'])
                    if exists:
                        # raise ValidationError('You have already registered for this team. Please Register with another team.')
                        return view_all_tournament(request,
                                                   'You have already registered for this tournament ' + str(
                                                       tournament_id) + '. Please Register with another one.')
                    team_obj = team_form.save(commit=False)
                    team_obj.login = user_wrapper
                    team_obj.tournament = tournament
                    team_obj.save()

                    # saving the list of players entered by user
                    count = SportsSpecification.objects.get(sport=tournament.sport).no_of_players
                    logger.debug("count of players submitted by user", count)
                    all_players = []
                    for i in range(count):
                        all_players.append(
                            Player(name=request.POST.get('player_name' + str(i + 1)),
                                   number=request.POST.get('player_number' + str(i + 1)),
                                   email=request.POST.get('player_email' + str(i + 1)),
                                   team=team_obj))
                    Player.objects.bulk_create(all_players)

                    # client = nexmo.Client(key=conf.nexmo_key, secret=conf.nexmo_secret)

                    # response = client.start_verification({'brand': 'SpoFit', 'number': '917559435851'})

                    # response = response['messages'][0]
                    # logger.debug(response)
                    # if response['status'] == '0':
                    #     logger.debug('Message sent', response['message-id'],'\nRemaining Balance: ',response['remaining-balance'])
                    # else:
                    #     logger.debug('Error: ', response['error-text'])
                    #


                    tournament.number_of_team += 1
                    tournament.save()
                    logger.debug(team_obj)
                    return HttpResponseRedirect('/dashboard/')
                else:
                    logger.debug(team_form.errors)
                    logger.debug(team_form.non_field_errors())
                    logger.debug("here")
                    return HttpResponse('Not Valid', team_form.errors)

            no_of_players = SportsSpecification.objects.get(sport=tournament.sport).no_of_players

            team_form = TeamForm(instance=team)
            player_form = PlayerForm()
            logger.debug(user)
            return render(request, 'home/register_team.html',
                          {'team_form': team_form,
                           'player_form': player_form,
                           'tournament_id': tournament_id,
                           'no_of_players': range(no_of_players)})
        else:
            return view_all_tournament(request, conf.email_verification_error)
    else:
        logger.debug('not logged in: register_tournament:else user')
        tournament_id = request.POST.get('tournament_id')
        # return render(request, 'home/register.html', {'ref': '/register/tournament/', 'tournament_id': request.POST.get('tournament_id')})
        return register(request, {'goto': '/view/'})


def verification_process(request, key, username):
    print('key= ' + key)
    print('username= ' + username)
    user = User.objects.get(username=username)
    if user.userwrapper.key == 'verified':
        return HttpResponseRedirect('/')
    if user:
        if user.userwrapper.key == key:
            user.userwrapper.key = 'verified'
            user.userwrapper.save()
            return HttpResponseRedirect('/')
        else:
            return HttpResponse('not verified ' + key + " ---- " + username)
    else:
        return HttpResponse('not verified: user not found ' + key + " ---- " + username)


def start_scheduling(request):
    print(request)
    print(request.POST)
    tournament_id = request.POST.get('tournament_id', 0)
    if tournament_id:
        tournament = Tournament.objects.get(pk=tournament_id)
        print(tournament.number_of_team)
        all_teams = list(tournament.team_set.all())
        number_of_teams = tournament.number_of_team
        matches_per_day = tournament.matches_per_day
        number_of_days = tournament.available_days
        type = tournament.type
        if type == 1:
            number_of_matches = (number_of_teams * (number_of_teams - 1) / 2)
            minimum_days = int(math.ceil(number_of_matches / matches_per_day))

            if number_of_days < minimum_days:
                return HttpResponse(
                    "Sorry Matches cant be schedule in " + str(
                        number_of_days) + " days but can be scheduled in " + str(
                        minimum_days))
            odd = False

            # new_user = LoginCredential(user_name=user_name, password=password, matches_per_day=matches_per_day,
            #                            number_of_team=number_of_teams, type=type, number_of_pool=1)
            # new_user.save()
            # new_pool = Pool(login=new_user, pool_number=1)
            # new_pool.save()
            # user_id = new_user.id
            if number_of_teams % 2 == 1:
                odd = True
                number_of_teams += 1
                all_teams.append('dummy_team')
                # group1=["pune warriors india","Mumbai Indian","King X1 punjab","Sunrise Hyderbad"]
                # group2=["Rising Pune Supergaints","Chennai king","Kolkalta Kinight rider","Delhi devils"]
            random.shuffle(all_teams)
            # group1 = all_teams[:]
            group1 = []
            group2 = []
            for i in range(0, int(number_of_teams / 2)):
                group1.append(all_teams[i])
                group2.append(all_teams[i + int(number_of_teams / 2)])

            print(group1)
            print(group2)
            list1 = []
            list2 = []
            for i in range(number_of_teams - 1):
                list1.extend(group1)
                list2.extend(group2)
                group1.insert(1, group2[0])
                group2.remove(group2[0])
                group2.append(group1[int(number_of_teams / 2)])
                group1.remove(group1[int(number_of_teams / 2)])

            all_new_teams = []
            pool = Pool(tournament=tournament, number_of_teams=tournament.number_of_team, pool_number=1)
            pool.save()
            print("GroupssSSSSsss", group1, group2)
            try:
                group1.pop(group1.index('dummy_team'))
            except:
                {}
            try:
                group2.pop(group2.index('dummy_team'))
            except:
                {}
            for team in group1:
                print('Start Scheduling:', all_new_teams)
                all_new_teams.append(Point(pool=pool, team=team))

            for team in group2:
                all_new_teams.append(Point(team=team, pool=pool))
            # Using bulk_create instead of saving team every time
            # It uses only one query to save all teams
            # Similarly for all the matches we used save n*(n-1)/2 times but now will use only 1 query
            # Very much optimized
            Point.objects.bulk_create(all_new_teams)

            # if not odd:
            #     new_team = Point(team=group2[len(group2) - 1], pool=pool)
            #     new_team.save()
            if odd:
                index = list1.index('dummy_team')
                while index or index == 0:
                    list1.pop(index)
                    list2.pop(index)
                    try:
                        index = list1.index('dummy_team')
                    except:
                        break

                index = list2.index('dummy_team')
                while index or index == 0:
                    list1.pop(index)
                    list2.pop(index)
                    try:
                        index = list2.index('dummy_team')
                    except:
                        break
            # all_matches = zip(list1,list2)
            # logger.debug(minimum_days)
            # logger.debug(matches_per_day)
            # logger.debug(list1)
            # logger.debug(list2)
            new_matches = []
            for i in range(len(list1)):
                new_matches.append(Match(team1=list1[i], team2=list2[i], pool=pool))
                # logger.debug(new_matches[i].id)
            Match.objects.bulk_create(new_matches)
            # match_id_list = list(Match.objects.filter(login=new_user).values_list('id', flat=True))
            # logger.debug(match_id_list)
            # Set user id for this session
            # Acess using (user_id = request.session['user_id'])
            match_obj_rows = pool.match_set
            match_id_list = match_obj_rows.values_list('id', flat=True)
            logger.debug(list1)
            return HttpResponse('/dashboard/')
            # Pool system
        elif type == 2:
            if number_of_teams >= 8:
                if number_of_teams % 3 == 0 or number_of_teams % 4 == 0 or number_of_teams % 5 == 0:

                    team_per_pool = int(number_of_teams / number_of_pool)
                    # if number_of_teams % 6 == 0:
                    #     team_per_pool = 6
                    # elif number_of_teams % 5 == 0:
                    #     team_per_pool = 5
                    # elif number_of_teams % 4 == 0:
                    #     team_per_pool = 4
                    # elif number_of_teams % 3 == 0:
                    #     team_per_pool = 3
                    # number_of_pool = int(number_of_teams / team_per_pool)

                    number_of_matches = int(
                        (team_per_pool * (team_per_pool - 1)) / 2) * number_of_pool
                    new_pool = []
                    new_points_table = []
                    for i in range(number_of_pool):
                        new_pool += [
                            Pool(tournament=tournament, pool_number=i + 1,
                                 number_of_teams=team_per_pool
                                 )]
                        # logger.debug(new_pool[i].pk)
                    Pool.objects.bulk_create(new_pool)
                    logger.debug(new_pool)
                    all_teams = []
                    for i in range(1, number_of_teams + 1):
                        all_teams.append("Team" + str(i))
                    # all_teams = group1 + group2
                    # logger.debug(all_teams)
                    all_pool = Pool.objects.filter(tournament=tournament)
                    for i in range(number_of_pool):
                        for j in range(team_per_pool):
                            # logger.debug(new_pool[i].id)
                            new_points_table += [Point(pool=all_pool[i], team=all_teams[i * team_per_pool + j])]
                            # logger.debug(str(i) + ' ' + all_teams[i * team_per_pool + j])
                    Point.objects.bulk_create(new_points_table)

                    new_matches = []
                    list1 = []
                    list2 = []
                    for i in range(number_of_pool):
                        zipped_list = round_robin(
                            list(Point.objects.filter(pool=all_pool[i]).values_list('team', flat=True)))
                        for team1, team2 in zipped_list:
                            logger.debug(team1 + "v/s" + team2)
                            list1.append(team1)
                            list2.append(team2)
                            new_matches.append(Match(pool=all_pool[i], team1=team1, team2=team2))

                    Match.objects.bulk_create(new_matches)
                    rows = int(math.floor(number_of_pool / 2))
                    extra = 0
                    if number_of_pool % 2 == 1:
                        extra = number_of_pool - 1

                    return HttpResponseRedirect('/dashboard/')

                else:
                    return HttpResponse("Number of teams should be multiple of 3 or 4 or 5")
            else:
                return HttpResponse("You need at least 8 teams for pool system")
    # Should never go here
    else:
        print('tournament id not found')
    return HttpResponse('Done scheduling')


def facebook_sign_in(request):
    print(request.user)
    if str(request.user) == 'AnonymousUser':
        return render(request, 'home/register.html', {'form': UserForm, 'info': 'Please Log in First.'})

    social_user = request.user.social_auth.filter(
        provider='facebook',
    ).first()
    logger.debug(social_user)
    if social_user:
        # url = "http://graph.facebook.com/" + social_user.uid + "/picture?type=large" % response['id']
        url = u'https://graph.facebook.com/{0}/' \
              u'?fields=id,name,location,picture,email' \
              u'&access_token={1}'.format(
            social_user.uid,
            social_user.extra_data['access_token'],
        )
        # response = urlopen(url)

        logger.debug(social_user.uid)
        logger.debug(social_user.extra_data['access_token'])
        # logger.debug(response)

        graph = facebook.GraphAPI(social_user.extra_data['access_token'])

        fields = graph.get_object(id='me?fields=email,id,name,picture')

        name = fields.get('name')
        email = fields.get('email')
        id = fields.get('id')

        image_url = 'http://graph.facebook.com/' + id + '/picture'

        print("from facebook: ", name, email, id, image_url)

        user = User.objects.filter(email=email).first()
        if not user:
            print('user doesnt exist for this facebook id, creating new...')
            user = User(username=id, first_name=name, email=email)
            user.save()
            user_wrapper = UserWrapper(user=user)
            user_wrapper.key = 'verified'
            user_wrapper.save()
            fb_user = FacebookUser(fb_id=id, user_wrapper=user_wrapper, image_url=image_url)
            fb_user.save()
        request.session.set_expiry(10 * 60)
        request.session['user_id'] = user.id
        return HttpResponseRedirect("/dashboard/")

    return None


def change_password(request):
    user = user_logged_in(request)
    if user:
        if request.method == 'POST':
            old = request.POST.get('old_pwd')
            new = request.POST.get('new_pwd')
            cnf = request.POST.get('cnf_pwd')
            # print("user:",User.objects.get(pk=user).username)

            n_user = authenticate(username = User.objects.get(pk=user).username , password = old )
            if n_user is None:
                return render(request, 'home/change_password.html', {
                    'error': "Invalid Old Password.",
                })
            else:
                if new != cnf:
                    print('new !=cnf')
                    return render(request, 'home/change_password.html', {
                        'error': "Confirm Password didn't match new Password!",
                    })
                else:
                    n_user.set_password(new)
                    n_user.save()
                    return render(request, 'home/dashboard.html', {
                        'success': "Password is successfully changed",
                    })
        else:
            return render(request, 'home/change_password.html')


    else:
        return register(request, {'goto': '/change_password/'})
        # return redirect('home:register', ref='/change_password/')

#
def forgot_password(request):
    user = user_logged_in(request)
    if not user:
        if request.method == 'POST':
            email = request.POST.get('email')
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return render(request, 'home/forgot_password.html', {'error': 'No User exist with '+email})
            new_user_wrapper = UserWrapper(user=user)
            print(user.email)
            new_user_wrapper.key = generate_activation_key()
            link = conf.site_initial_link + '/verification/email/' + new_user_wrapper.key + \
                   '/' + user.username
            if email_sending_service_enabled:
                send_mail('SpoFit Email Verification',
                          link,
                          'akzarma2@gmail.com',
                          [user.email], fail_silently=False)
                return render(request, 'home/register.html',
                              {'success':'Mail has been successfully sent to '+email,
                               'form':UserForm})
            else:
                return render(request, 'home/forgot_password.html', {'error': 'Mail service is temporarily out of coverage.'})

        else:
            return render(request, 'home/forgot_password.html')
    else:
        return HttpResponseRedirect('/dashboard/')
