from django.urls import path
from logic import views


# app_name = 'logic'

urlpatterns = [
    path('', views.index, name='landing'),
    path('index', views.index, name='index'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('signup', views.signup, name='signup'),
    path('counter', views.counter, name='counter'),
    path('create_game', views.create_game, name='create_game'),
    path('get_move', views.get_move, name='get_move'),
    path('game_status', views.game_status, name='game_status'),
    path('select_game/<str:action>', views.select_game, name='select_game'),
    path('select_game/<str:action>/<int:game_id>', views.select_game, name='select_game'),
    path('show_game', views.show_game, name='show_game'),
    path('move', views.move, name='move'),
]
