from django.contrib import admin
from .models import Match,Point,Pool,Tournament

admin.site.register(Point)
admin.site.register(Tournament)
admin.site.register(Match)
admin.site.register(Pool)
