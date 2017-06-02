import math

from django.shortcuts import render, HttpResponse


# Create your views here.

def get_information(request):
    return render(request, 'home/information.html')


def schedule(request):
    group1 = []
    group2 = []
    list1 = []
    list2 = []
    number_of_teams = int(request.GET.get('number_of_teams'))
    number_of_days = int(request.GET.get('number_of_days'))
    matches_per_day = int(request.GET.get('matches_per_day'))
    number_of_matches = (number_of_teams * (number_of_teams - 1) / 2)
    minimum_days = int(math.ceil(number_of_matches / matches_per_day))
    if number_of_days < minimum_days:
        return HttpResponse(
            "Sorry Matches cant be schedule in " + str(number_of_days) + " days but can be scheduled in " + str(
                minimum_days))
    odd = False
    if number_of_teams % 2 == 1:
        odd = True
        number_of_teams += 1
    # group1=["pune warriors india","Mumbai Indian","King X1 punjab","Sunrise Hyderbad"]
    # group2=["Rising Pune Supergaints","Chennai king","Kolkalta Kinight rider","Delhi devils"]
    for i in range(1, int(number_of_teams / 2) + 1):
        group1.append("Team" + str(i))
        group2.append("Team" + str(i + int(number_of_teams / 2)))

    print(group1)
    print(group2)
    for i in range(number_of_teams - 1):
        list1.extend(group1)
        list2.extend(group2)
        group1.insert(1, group2[0])
        group2.remove(group2[0])

        group2.append(group1[int(number_of_teams / 2)])
        group1.remove(group1[int(number_of_teams / 2)])
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
    print(minimum_days)
    print(matches_per_day)
    print(list1)
    print(list2)
    return render(request, 'home/schedule.html',
                  {
                      'number_of_days': range(minimum_days),
                      'matches_per_day_list': range(matches_per_day), 'list1': list1, 'list2': list2,
                      'matches_per_day':matches_per_day,
                  })
