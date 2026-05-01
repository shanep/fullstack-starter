from django.contrib import admin
from django.urls import path
from hello import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_view, name='index'),                     # http://35.90.198.162/
    path('hello/', views.hello_world, name='hello'),              # http://35.90.198.162/hello/
    path('hello/register/', views.register_view, name='register'),  # http://35.90.198.162/hello/register/
    path('hello/login/', views.login_view, name='login'),         # http://35.90.198.162/hello/login/
    path('hello/tic_tac_toe', views.tic_tac_toe_view, name='tic_tac_toe'),  # http://35.90.198.162/hello/tic_tac_toe
    path('hello/logout/', views.logout_view, name='logout'),      # http://35.90.198.162/hello/logout/
    path('hello/directory/', views.game_directory_view, name='game_directory'),  # http://35.90.198.162/hello/directory/
    path('hello/statistics', views.statistics_view, name='statistics')  # http://35.90.198.162/hello/statistcs/
]