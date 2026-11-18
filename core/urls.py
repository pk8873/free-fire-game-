from django.urls import path
from . import views

urlpatterns=[
    path('',views.home,name='home'),
    path('signup/',views.signup_view,name='signup'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('teams/create/',views.create_team,name='create-team'),
    path('teams/join/',views.join_team,name='join-team'),
    path('tournaments/<slug:slug>/',views.tournament_detail,name='tournament-detail'),
    path('tournaments/<slug:slug>/register/',views.register_team,name='register-team'),
    path('matches/',views.matches,name='matches'),
    path('matches/<int:match_id>/result/',views.submit_result,name='submit-result'),
    path('matches/<int:match_id>/result/',views.submit_result,name='submit-result'),
    path('matches/<int:match_id>/dispute/',views.file_dispute,name='file-dispute'),
    path('manifest.webmanifest',views.manifest,name='manifest'),
    path('service-worker.js',views.service_worker,name='service-worker'),
]
