from django import template

register = template.Library()


@register.simple_tag()
def lookup(d, key1, key2, matches):
    return d[key1 * matches + key2]


@register.simple_tag()
def test(d, key1, key2, matches):
    try:
        d[key1 * matches + key2]
    except:
        return False
    return True
