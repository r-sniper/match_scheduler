import json
import math
import urllib
# from urllib.request import urlopen

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse, get_object_or_404

from .forms import TournamentForm, UserForm, TeamForm
from .models import Tournament, Point, Pool, UserWrapper, GoogleUser, Team


def user_logged_in(request):
    user_id = request.session.get('user_id', 0)
    if not user_id:
        return 0
    else:
        return user_id


# Add a tournament
def get_information(request):
    user_id = user_logged_in(request)
    # If user exists then he can add tournament
    if user_id:
        if request.method == "POST":
            print('post in get_information')
            form = TournamentForm(request.POST)
            if form.is_valid():
                tournament = form.save(commit=False)
                user_obj = User.objects.get(pk=user_id)
                user_wrapper = user_obj.userwrapper
                tournament.login = user_wrapper
                print(user_wrapper.user.username)
                type_of_match = form.cleaned_data.get('match_type')
                avalaible_hrs = form.cleaned_data.get("available_hrs")
                match_duration = form.cleaned_data.get("match_duration")
                break_duration = form.cleaned_data.get("break_duration")

                tournament.matches_per_day = (int)(avalaible_hrs / (match_duration + break_duration))
                print("mathes per day" + str(tournament.matches_per_day))

                type = 1
                if type_of_match == 'Pool Match':
                    type = 2
                tournament.type = type
                tournament.save()
                group1 = []
                group2 = []
                list1 = []
                list2 = []
                user_name = user_obj.username

                # number_of_teams = tournament.number_of_team
                number_of_days = tournament.available_days
                matches_per_day = tournament.matches_per_day
                number_of_pool = tournament.number_of_pool
                # Our conventions
                # 1. League matches
                # 2. Pool System
                # 3. Knockout

                # League matches
                print("scheduling")
                print(type)

                # print(Pool.objects.filter(login=user_wrapper))
                # print(user_wrapper.pool_set.all()   )
                return HttpResponseRedirect('/dashboard/')
            else:
                print("else " + str(form.errors))
        else:
            form = TournamentForm()
            print('not post in get_information')
        return render(request, 'home/information.html', {
            'form': form,
            'logged_in': True
        })
    else:
        return render(request, 'home/home_page.html', {
            'logged_in': False
        })


def dashboard(request):
    user_id = user_logged_in(request)
    print('dashboard', request.session.get('user', 0))
    if user_id:
        user = User.objects.get(pk=user_id)
        user_wrapper = user.userwrapper
        tournament = user_wrapper.tournament_set.all()
        number_of_pool = 0

        if tournament:
            print(tournament[0])
            print("Tournament exists")
        return render(request, 'home/dashboard.html', {
            'logged_in': True,
            'tournament': tournament
        })
    else:
        social_user = request.user.social_auth.filter(
            provider='facebook',
        ).first()
        print(social_user)
        if social_user:
            # url = "http://graph.facebook.com/" + social_user.uid + "/picture?type=large" % response['id']
            url = u'https://graph.facebook.com/{0}/' \
                  u'?fields=id,name,location,picture,email' \
                  u'&access_token={1}'.format(
                social_user.uid,
                social_user.extra_data['access_token'],
            )
            # response = urlopen(url)
            print(social_user.uid)
            print(social_user.extra_data['access_token'])
            # print(response)
            print(social_user.extra_data)
            response = urllib.request.Request(url)
            print(response)
            user = str(urllib.urlopen(response).read(), 'utf-8')
            print(user)
            user_to_json = json.loads(user)
            name = user_to_json['name']
            email = user_to_json['email']
            id = user_to_json['id']
            return HttpResponse("here")
        return render(request, 'home/home_page.html', {
            'logged_in': False
        })


def register(request):
    if user_logged_in(request):
        return HttpResponseRedirect('/dashboard/')
    if request.method == "POST":
        print("register")
        form = UserForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user.set_password(new_user.password)
            new_user.save()
            new_user_wrapper = UserWrapper(user=new_user)
            new_user_wrapper.save()
            request.session.set_expiry(10 * 60)
            request.session['user_id'] = new_user.id
            print(User.objects.get(pk=new_user.pk).first_name)
            return HttpResponseRedirect('/dashboard/')
        else:
            print("Form was not valid because of" + str(form.errors))
    else:
        form = UserForm()
    return render(request, 'home/register.html', {
        'form': form,
        'logged_in': False
    })


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
        print('HeLlO')
        text = request.POST.get('winner_name').split(' ')
        match_id = text[1]
        winner = text[0]
        user_id = request.session['user_id']
        user_obj = User.objects.get(id=user_id)
        user_wrapper = user_obj.userwrapper
        print(winner)
        print(user_id)
        # if not needed(will review it later)
        if request.is_ajax:
            tournament = user_wrapper.tournament_set.all()
            current_tournament = tournament[tournament_number]
            print('pool number' + str(pool_number))
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
            print('Saving now')
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
        # print("submit")
        type = 0
        user_id = user_logged_in(request)
        if not user_id:
            return HttpResponseRedirect('/')
        user_obj = User.objects.get(id=user_id)
        user_wrapper = user_obj.userwrapper
        tournament_obj = user_wrapper.tournament_set.all()
        print(tournament_obj)
        print('tournament' + str(tournament_number))
        print('pool' + str(pool_number))

        user_name = user_obj.username
        current_tournament = tournament_obj[tournament_number]
        number_of_pool = current_tournament.number_of_pool
        number_of_teams = current_tournament.number_of_team
        pool_obj = current_tournament.pool_set.all()

        # show schedule for that pool
        if number_of_pool == 1 or pool_number:
            if pool_number == 0:
                print("pool number was zero")
                print("Setting it ot one")
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
            print(list1)
            print(number_of_teams)
            return render(request, 'home/schedule.html/',
                          {
                              'number_of_days': range(minimum_days),
                              'matches_per_day_list': range(matches_per_day), 'list1': list1, 'list2': list2,
                              'match_id': match_id_list,
                              'matches_per_day': matches_per_day, 'user_name': user_name, 'user_id': user_id,
                              'number_of_pool': number_of_pool,
                              'pool_number': pool_number,
                              'tournament_number': tournament_number,
                              'logged_in': True
                          })
        # Show all pools
        else:
            rows = int(math.floor(number_of_pool / 2))
            print("Number of teams(Points table):" + str(number_of_teams))
            print("Number of pool(Points table):" + str(number_of_pool))
            print("Number of teams(Points table):" + str(pool_obj[0].number_of_teams))
            team_per_pool = int(number_of_teams / number_of_pool)
            all_teams = []
            for pool in pool_obj:
                all_teams += pool.point_set.values_list('team', flat=True)
            print(all_teams)
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
                'logged_in': True
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
    send_mail(subject, message, from_email, to_email, fail_silently=False)

    return HttpResponse("Successfully send")


# Basic home page(information about spofit)
def home_page(request):
    ref = '/dashboard/'
    print(request.method)
    # print(request.session.get_expiry_age())
    if request.method == "POST":

        user_name = request.POST.get('uname')
        password = request.POST.get('pass')
        user = authenticate(username=user_name, password=password)
        if user is not None:
            user_obj = User.objects.get(username=user)
            request.session.set_expiry(10 * 60)
            request.session['user_id'] = user_obj.id
            if not request.POST.get('ref') == '':
                ref = request.POST.get('ref')
                return register_tournament(request, request.POST.get('tournament_id'))
            else:
                return HttpResponseRedirect(ref)

        else:
            print("Doesn't")
            return HttpResponse('<h1>First Sign Up for this service</h1>')

    else:
        print(request.session.get_expiry_age())
        user_id = request.session.get('user_id', 0)
        print(request.session.get_expiry_age())
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
    user_id = request.session['user_id']
    if user_id:
        user_obj = User.objects.get(pk=user_id)
        # print(user_id)
        user_wrapper = user_obj.userwrapper
        tournament_obj = user_wrapper.tournament_set.all()
        current_tournament = tournament_obj[tournament_number]
        pool_obj = current_tournament.pool_set.get(pool_number=pool_number)
        print("Hello")
        print(pool_obj.pool_number)
        number_of_pool = current_tournament.number_of_pool
        full_table = pool_obj.point_set.order_by('-wins').all
        print(full_table)
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
    # print(list3)
    return list3


def google_sign_in(request):
    if request.is_ajax:
        print("Got google data")
        id = request.POST.get('id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        image = request.POST.get('image')
        print(id, email, image, name)
        # Use doesn't exists just set session
        user = User.objects.filter(email=email).first()
        if not user:
            print('user doesnt exist')
            user = User(first_name=name, email=email)
            user.save()
            user_wrapper = UserWrapper(user=user)
            user_wrapper.save()
            google_user = GoogleUser(google_id=id, user_wrapper=user_wrapper, image_url=image)
            google_user.save()
        request.session.set_expiry(10 * 60)
        request.session['user_id'] = user.id
        return HttpResponse("true")




        # if type == 1:
        #                    number_of_matches = (number_of_teams * (number_of_teams - 1) / 2)
        #                    minimum_days = int(math.ceil(number_of_matches / matches_per_day))
        #
        #                    if number_of_days < minimum_days:
        #                        return HttpResponse(
        #                            "Sorry Matches cant be schedule in " + str(
        #                                number_of_days) + " days but can be scheduled in " + str(
        #                                minimum_days))
        #                    odd = False
        #
        #                    # new_user = LoginCredential(user_name=user_name, password=password, matches_per_day=matches_per_day,
        #                    #                            number_of_team=number_of_teams, type=type, number_of_pool=1)
        #                    # new_user.save()
        #                    # new_pool = Pool(login=new_user, pool_number=1)
        #                    # new_pool.save()
        #                    # user_id = new_user.id
        #                    if number_of_teams % 2 == 1:
        #                        odd = True
        #                        number_of_teams += 1
        #                    # group1=["pune warriors india","Mumbai Indian","King X1 punjab","Sunrise Hyderbad"]
        #                    # group2=["Rising Pune Supergaints","Chennai king","Kolkalta Kinight rider","Delhi devils"]
        #                    for i in range(1, int(number_of_teams / 2) + 1):
        #                        group1.append("Team" + str(i))
        #                        group2.append("Team" + str(i + int(number_of_teams / 2)))
        #
        #                    # print(group1)
        #                    # print(group2)
        #                    for i in range(number_of_teams - 1):
        #                        list1.extend(group1)
        #                        list2.extend(group2)
        #                        group1.insert(1, group2[0])
        #                        group2.remove(group2[0])
        #                        group2.append(group1[int(number_of_teams / 2)])
        #                        group1.remove(group1[int(number_of_teams / 2)])
        #
        #                    all_new_teams = []
        #                    pool = Pool(tournament=tournament, number_of_teams=number_of_teams, pool_number=1)
        #                    pool.save()
        #                    for team in group1:
        #                        all_new_teams.append(Point(pool=pool, team=team))
        #
        #                    for team in group2[:-1]:
        #                        all_new_teams.append(Point(team=team, pool=pool))
        #                    # Using bulk_create instead of saving team every time
        #                    # It uses only one query to save all teams
        #                    # Silimarly for all the matches we used save n*(n-1)/2 times but now will use only 1 query
        #                    # Very much optimized
        #                    Point.objects.bulk_create(all_new_teams)
        #
        #                    if not odd:
        #                        new_team = Point(team=group2[len(group2) - 1], pool=pool)
        #                        new_team.save()
        #                    if odd:
        #                        index = list1.index("Team" + str(number_of_teams))
        #                        while index:
        #                            list1.pop(index)
        #                            list2.pop(index)
        #                            try:
        #                                index = list1.index("Team" + str(number_of_teams))
        #                            except:
        #                                break
        #
        #                        index = list2.index("Team" + str(number_of_teams))
        #                        while index:
        #                            list1.pop(index)
        #                            list2.pop(index)
        #                            try:
        #                                index = list2.index("Team" + str(number_of_teams))
        #                            except:
        #                                break
        #                    # all_matches = zip(list1,list2)
        #                    # print(minimum_days)
        #                    # print(matches_per_day)
        #                    # print(list1)
        #                    # print(list2)
        #                    new_matches = []
        #                    for i in range(len(list1)):
        #                        new_matches.append(Match(team1=list1[i], team2=list2[i], pool=pool))
        #                        # print(new_matches[i].id)
        #                    Match.objects.bulk_create(new_matches)
        #                    # match_id_list = list(Match.objects.filter(login=new_user).values_list('id', flat=True))
        #                    # print(match_id_list)
        #                    # Set user id for this session
        #                    # Acess using (user_id = request.session['user_id'])
        #                    match_obj_rows = pool.match_set
        #                    match_id_list = match_obj_rows.values_list('id', flat=True)
        #                    print(list1)
        #                    return HttpResponseRedirect('/dashboard/')
        #                # Pool system
        #                elif type == 2:
        #                    if number_of_teams >= 8:
        #                        if number_of_teams % 3 == 0 or number_of_teams % 4 == 0 or number_of_teams % 5 == 0:
        #
        #                            team_per_pool = int(number_of_teams / number_of_pool)
        #                            # if number_of_teams % 6 == 0:
        #                            #     team_per_pool = 6
        #                            # elif number_of_teams % 5 == 0:
        #                            #     team_per_pool = 5
        #                            # elif number_of_teams % 4 == 0:
        #                            #     team_per_pool = 4
        #                            # elif number_of_teams % 3 == 0:
        #                            #     team_per_pool = 3
        #                            # number_of_pool = int(number_of_teams / team_per_pool)
        #
        #                            number_of_matches = int(
        #                                (team_per_pool * (team_per_pool - 1)) / 2) * number_of_pool
        #                            new_pool = []
        #                            new_points_table = []
        #                            for i in range(number_of_pool):
        #                                new_pool += [
        #                                    Pool(tournament=tournament, pool_number=i + 1,
        #                                         number_of_teams=team_per_pool
        #                                         )]
        #                                # print(new_pool[i].pk)
        #                            Pool.objects.bulk_create(new_pool)
        #                            print(new_pool)
        #                            all_teams = []
        #                            for i in range(1, number_of_teams + 1):
        #                                all_teams.append("Team" + str(i))
        #                            # all_teams = group1 + group2
        #                            # print(all_teams)
        #                            all_pool = Pool.objects.filter(tournament=tournament)
        #                            for i in range(number_of_pool):
        #                                for j in range(team_per_pool):
        #                                    # print(new_pool[i].id)
        #                                    new_points_table += [Point(pool=all_pool[i], team=all_teams[i * team_per_pool + j])]
        #                                    # print(str(i) + ' ' + all_teams[i * team_per_pool + j])
        #                            Point.objects.bulk_create(new_points_table)
        #
        #                            new_matches = []
        #                            list1 = []
        #                            list2 = []
        #                            for i in range(number_of_pool):
        #                                zipped_list = round_robin(
        #                                    list(Point.objects.filter(pool=all_pool[i]).values_list('team', flat=True)))
        #                                for team1, team2 in zipped_list:
        #                                    print(team1 + "v/s" + team2)
        #                                    list1.append(team1)
        #                                    list2.append(team2)
        #                                    new_matches.append(Match(pool=all_pool[i], team1=team1, team2=team2))
        #
        #                            Match.objects.bulk_create(new_matches)
        #                            rows = int(math.floor(number_of_pool / 2))
        #                            extra = 0
        #                            if number_of_pool % 2 == 1:
        #                                extra = number_of_pool - 1
        #
        #                            return HttpResponseRedirect('/dashboard/')
        #
        #                        else:
        #                            return HttpResponse("Number of teams should be multiple of 3 or 4 or 5")
        #                    else:
        #                        return HttpResponse("You need at least 8 teams for pool system")


def view_all_tournament(request):
    return render(request, 'home/view_tournaments.html', {
        'all_tournaments': Tournament.objects.all()
    })


def register_tournament(request, tournament_id=-1):
    user = user_logged_in(request)
    print("Method123:"+request.method)



    # return HttpResponse("Here")
    if user:
        if not request.POST.get('tournament_id') == '':
            tournament_id = request.POST.get('tournament_id')

        tournament = get_object_or_404(Tournament, pk=tournament_id)
        user_obj = User.objects.get(pk=user)
        user_wrapper = user_obj.userwrapper
        team = Team(login=user_wrapper, tournament=tournament)
        # team.login = user_wrapper
        # team.tournament = tournament

        team_form = TeamForm(instance=team)
        print(user)
        return render(request, 'home/register_tournament.html', {'team_form': team_form})
    else:
        print('not logged in: register_tournament:else user')
        return render(request, 'home/register.html', {'ref': '/register/tournament/', 'tournament_id': request.POST.get('tournament_id')})
