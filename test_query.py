import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'ratonGato.settings')
django.setup()

from datamodel.models import Game, Move
from django.contrib.auth.models import User


def test_query():
    # Check if there is an user with id=10 and if it does not exists, creat it
    u10 = User.objects.get_or_create(id=10, username="u10")[0]
    u10.save()
    # Check if there is an user with id=11 and if it does not exists, creat it
    u11 = User.objects.get_or_create(id=11, username="u11")[0]
    u11.save()
    # Create a game and assign it to the user with id=10
    game = Game(cat_user=u10)
    game.save()
    # Search for all games with only one user assigned
    # We sort it at the same time by id
    g_1u = Game.objects.filter(mouse_user=None).order_by('id')
    for g in g_1u:
        print(g)
    # Assign a second user to the game and start it
    curr_game = g_1u[0]
    curr_game.mouse_user = u11
    curr_game.save()
    print(curr_game)
    # Add moves to the game
    move1 = Move(game=curr_game, origin=2, target=11,
                 player=curr_game.cat_user)
    move1.save()
    # curr_game.cat2 = 11
    # curr_game.cat_turn = False
    # curr_game.save()
    print(curr_game)
    move2 = Move(game=curr_game, origin=59, target=52,
                 player=curr_game.mouse_user)
    move2.save()
    # curr_game.mouse = 52
    # curr_game.cat_turn = True
    # curr_game.save()
    print(curr_game)


# Start execution here!
if __name__ == '__main__':
    print('Starting Mouse&Cats query test script...')
    test_query()
