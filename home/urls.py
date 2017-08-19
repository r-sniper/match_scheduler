from django.conf.urls import url

from . import views

app_name = 'home'

urlpatterns = [

    # Register User
    url(r'^register/$', views.register, name="register"),
    # - Get Information from user
    url(r'^information/$', views.get_information, name="get_information"),
    # - Dashboard
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    # /-Sends to home page
    url(r'^$', views.home_page, name="home_page"),

    # /schedule - Get Information from user
    url(r'^schedule/(?P<tournament_number>[0-9]+)/$', views.schedule, name="schedule"),
    # /test_send_email
    url(r'^test_send_email/$', views.test_send_email, name='test_send_email'),
    # /points_table/tournament number)/(pool_number) - Gets the points table
    url(r'^points_table/(?P<tournament_number>[0-9]+)/(?P<pool_number>[0-9]+)/$', views.points_table,
        name='points_table'),
    # /schedule/(tournament number)/(pool_number)
    url(r'^schedule/(?P<tournament_number>[0-9]+)/(?P<pool_number>[0-9]+)/$', views.schedule, name="pool_schedule"),
    # /logout
    url(r'^logout/$', views.logout, name="logout"),
    # /google_sign_in
    url(r'^google_sign_in/$', views.google_sign_in, name='google_sign_in'),

    url(r'^view/$', views.view_all_tournament, name='view_all_tournament'),

    url(r'^tournament/register/(?P<tournament_id>[0-9]+)$', views.register_tournament, name='register_tournament'),

    url(r'^register/(?P<ref>.+)$', views.register, name="register"),

    # url(r'register/tournament/success$', views.registered_tournament, name='registered_tournament')

]
