from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello_world, name='hello'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('tic_tac_toe/', views.tic_tac_toe_view, name='tic_tac_toe'),
    path('logout/', views.logout_view, name='logout'),
    path('directory/', views.game_directory_view, name='game_directory'),
    path('statistics',views.statistics_view, name='statistics')
]