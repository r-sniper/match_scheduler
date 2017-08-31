from django.contrib import admin

from .models import Match, Point, Pool, Tournament, UserWrapper, Team, Category, Player, SportSpecification

admin.site.register(UserWrapper)
admin.site.register(Point)
admin.site.register(Tournament)
admin.site.register(Match)
admin.site.register(Pool)
admin.site.register(Team)
admin.site.register(Category)
admin.site.register(Player)
admin.site.register(SportSpecification)
