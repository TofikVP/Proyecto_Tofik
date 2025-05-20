from django import template

register = template.Library()

@register.filter
def average_stars(ratings):
    total = sum(r.stars for r in ratings)
    count = ratings.count()
    return total / count if count else 0

@register.simple_tag
def star_states(avg):
    """
    Devuelve una lista de 5 valores: 'full', 'half', 'empty'
    según el promedio de estrellas.
    """
    states = []
    for i in range(1, 6):
        if avg >= i:
            states.append('full')
        elif avg >= i - 0.5:
            states.append('half')
        else:
            states.append('empty')
    return states