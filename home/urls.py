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

    url(r'^team/register/$', views.register_team, name='register_team'),

    url(r'^register/(?P<ref>.+)$', views.register, name="register"),

    url(r'^verification/email/(?P<key>[\w]+)/(?P<username>[\w]+)', views.verification_process,
        name="verification_process"),

    url(r'^verification/resend/$', views.resend_mail, name='resend_mail'),

    url(r'^start_scheduling/$', views.start_scheduling, name='start_scheduling'),

    url(r'^facebook_sign_in/$', views.facebook_sign_in, name='facebook_sign_in'),

    url(r'^change_password/$', views.change_password, name='change_password'),

    url(r'^forgot_password$', views.forgot_password, name='forgot_password'),


]
