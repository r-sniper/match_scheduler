from django.contrib import admin
from .models import LoginCredential, Point, Match

admin.site.register(LoginCredential)
admin.site.register(Point)
admin.site.register(Match)
