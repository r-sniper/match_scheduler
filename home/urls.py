from django.conf.urls import url
from . import views

app_name = 'home'

urlpatterns = [
    # - Get Information from user
    url(r'^$', views.get_information, name="get_information"),
    #/schedule - Get Information from user
    url(r'^/schedule$', views.schedule, name="schedule"),


]
