from django.contrib import admin
from .models import LoginCredential,Match,Point,Pool

admin.site.register(LoginCredential)
admin.site.register(Point)
admin.site.register(Match)
admin.site.register(Pool)
