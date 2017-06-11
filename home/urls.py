from django.conf.urls import url
from . import views

app_name = 'home'

urlpatterns = [
    # - Get Information from user
    url(r'^information/$', views.get_information, name="get_information"),

    # /-Sends to home page
    url(r'^$', views.home_page, name="home_page"),
    # /schedule - Get Information from user
    url(r'schedule/$', views.schedule, name="schedule"),
    # /test_send_email
    url(r'test_send_email/$', views.test_send_email, name='test_send_email'),
    # /points_table - Gets the points table
    url(r'points_table/$', views.points_table, name='points_table'),


]
