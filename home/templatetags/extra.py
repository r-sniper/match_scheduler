from django import template

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
