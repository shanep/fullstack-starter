from django.contrib import admin
from django.urls import path
from hello import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_view, name='index'),
    path('hello/', views.hello_world, name='hello'),
    path('hello/register/', views.register_view, name='register'),
    path('hello/login/', views.login_view, name='login'),
    path('hello/tic_tac_toe', views.tic_tac_toe_view, name='tic_tac_toe'),
    path('hello/logout/', views.logout_view, name='logout'),
    path('hello/directory/', views.game_directory_view, name='game_directory'),
    path('hello/play/<str:variant_name>/', views.play_game, name='play_game'),
]