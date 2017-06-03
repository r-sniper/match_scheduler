import math
from .models import LoginCredential, Point, Match
from django.shortcuts import render, HttpResponse


# Create your views here.

def get_information(request):
    return render(request, 'home/information.html')


def schedule(request):
    if request.POST.get('submit'):
        group1 = []
        group2 = []
        list1 = []
        list2 = []
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')
        number_of_teams = int(request.POST.get('number_of_teams'))
        number_of_days = int(request.POST.get('number_of_days'))
        matches_per_day = int(request.POST.get('matches_per_day'))
        number_of_matches = (number_of_teams * (number_of_teams - 1) / 2)
        minimum_days = int(math.ceil(number_of_matches / matches_per_day))
        if number_of_days < minimum_days:
            return HttpResponse(
                "Sorry Matches cant be schedule in " + str(number_of_days) + " days but can be scheduled in " + str(
                    minimum_days))
        odd = False

        new_user = LoginCredential(user_name=user_name, password=password, matches_per_day=matches_per_day,
                                   number_of_team=number_of_teams)
        new_user.save()

        if number_of_teams % 2 == 1:
            odd = True
            number_of_teams += 1
        # group1=["pune warriors india","Mumbai Indian","King X1 punjab","Sunrise Hyderbad"]
        # group2=["Rising Pune Supergaints","Chennai king","Kolkalta Kinight rider","Delhi devils"]
        for i in range(1, int(number_of_teams / 2) + 1):
            group1.append("Team" + str(i))
            group2.append("Team" + str(i + int(number_of_teams / 2)))

        # print(group1)
        # print(group2)
        for i in range(number_of_teams - 1):
            list1.extend(group1)
            list2.extend(group2)
            group1.insert(1, group2[0])
            group2.remove(group2[0])

            group2.append(group1[int(number_of_teams / 2)])
            group1.remove(group1[int(number_of_teams / 2)])

        for team in group1:
            new_team = Point(team=team, login=new_user)
            new_team.save()
        for team in group2[:-1]:
            new_team = Point(team=team, login=new_user)
            new_team.save()

        if not odd:
            new_team = Point(team=group2[len(group2) - 1], login=new_user)
            new_team.save()
        if odd:
            index = list1.index("Team" + str(number_of_teams))
            while index:
                list1.pop(index)
                list2.pop(index)
                try:
                    index = list1.index("Team" + str(number_of_teams))
                except:
                    break

            index = list2.index("Team" + str(number_of_teams))
            while index:
                list1.pop(index)
                list2.pop(index)
                try:
                    index = list2.index("Team" + str(number_of_teams))
                except:
                    break
        # all_matches = zip(list1,list2)
        # print(minimum_days)
        # print(matches_per_day)
        # print(list1)
        # print(list2)

        for i in range(len(list1)):
            new_match = Match(team1=list1[i], team2=list2[i], login=new_user)
            new_match.save()
        match_id_list = list(Match.objects.filter(login=new_user).values_list('id', flat=True))
        print(match_id_list)
        return render(request, 'home/schedule.html',
                      {
                          'number_of_days': range(minimum_days),
                          'matches_per_day_list': range(matches_per_day), 'list1': list1, 'list2': list2,
                          'match_id': match_id_list,
                          'matches_per_day': matches_per_day, 'user_name': user_name,
                      })
    elif request.POST.get('winner'):
        print('This is POST method(Select Winner)')
        user_name = request.POST.get('get_user_name')
        print(user_name)
        winner_text = request.POST.get('winner').split(' ')
        winner = winner_text[0]

        print(winner)
        # user id not used yet but will(maybe) in future for optimizations
        user_obj = LoginCredential.objects.get(user_name=user_name)
        match_id = int(winner_text[1])
        print(match_id)
        match_obj_rows = user_obj.match_set
        match_obj = match_obj_rows.get(id=match_id)
        if match_obj.winner == '0':
            point_obj = Point.objects.get(login=user_obj, team=winner)
            point_obj.wins += 2
            point_obj.save()
        if match_obj.team1 == winner:
            match_obj.winner = '1'
        else:
            match_obj.winner = '2'
        match_obj.save()
        matches_per_day = user_obj.matches_per_day
        number_of_teams = user_obj.number_of_team
        number_of_days = int((number_of_teams * (number_of_teams - 1)) / 2)
        list1 = list(match_obj_rows.values_list('team1', flat=True))
        list2 = list(match_obj_rows.values_list('team2', flat=True))
        match_id_list = match_obj_rows.values_list('id', flat=True)
        if winner:
            return render(request, 'home/schedule.html',
                          {
                              'number_of_days': range(number_of_days),
                              'matches_per_day_list': range(matches_per_day), 'list1': list1, 'list2': list2,
                              'match_id': match_id_list,
                              'matches_per_day': matches_per_day, 'user_name': user_name,
                          })
        else:
            return HttpResponse("Error")

    else:
        return HttpResponse("Something went wrong")
