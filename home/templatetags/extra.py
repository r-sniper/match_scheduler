from django import template
from ..models import Match, Pool

register = template.Library()


@register.simple_tag()
def lookup(d, key1, key2, matches, key3=0):
    return d[key3 * 2 * matches + int(key1) * matches + int(key2)]


@register.simple_tag()
def lookup_match_id(d, key1):
    return d[key1]


@register.simple_tag()
def index_calculator(i, j, col):
    return (i * col + j + 1)


@register.simple_tag()
def test(d, key1, key2, matches):
    try:
        d[key1 * matches + key2]
    except:
        return False
    return True


@register.simple_tag()
def selected_winner(list1, list2, key1, key2, pool_id, matches, key3=0):
    team1 = list1[key3 * 2 * matches + int(key1) * matches + int(key2)]
    team2 = list2[key3 * 2 * matches + int(key1) * matches + int(key2)]
    pool_obj = Pool.objects.get(pk=int(pool_id))
    if (Match.objects.get(pool=pool_obj, team1=team1, team2=team2).winner == '0'):
        return False
    else:
        return True
