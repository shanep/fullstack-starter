# hello/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello_world, name='hello'),
    path('index/', views.index_view, name='index'),
    
    # CHANGE THIS LINE: from 'games/' to 'directory/'
    path('directory/', views.game_directory_view, name='game_directory'), 
    
    path('play/<str:variant_name>/', views.play_game, name='play_game'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('history/', views.game_history_view, name='game_history'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('tic_tac_toe/', views.tic_tac_toe_view, name='tic_tac_toe'),
]