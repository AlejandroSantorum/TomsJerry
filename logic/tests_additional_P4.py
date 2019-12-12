"""
"""

from django.core.exceptions import ValidationError
from django.urls import reverse

from datamodel import tests
from datamodel.models import Game, GameStatus, Move
from decimal import Decimal
from logic.tests_services import PlayGameBaseServiceTests, SHOW_GAME_SERVICE,\
                                 SELECT_GAME_SERVICE, SHOW_GAME_TITLE
from logic.tests_services import ServiceBaseTest, SIGNUP_TITLE, SERVICE_DEF,\
                                 SIGNUP_SERVICE, LOGIN_SERVICE
from logic.tests_services import USER_SESSION_ID, LOGOUT_SERVICE,\
                                 LANDING_TITLE, MOVE_SERVICE

# from logic.tests_services import *

INDEX_SERVICE = 'index'
PLAY_GAME_INVALID_MOVE = "play_invalid"

SERVICE_DEF[SIGNUP_SERVICE] = {
    "title": SIGNUP_TITLE,
    "pattern": r"Signup user"
}

SERVICE_DEF[INDEX_SERVICE] = {
    "title": LANDING_TITLE,
    "pattern": r"Login|Logout|Signup|Counter|Create game|Select game"
}

SERVICE_DEF[PLAY_GAME_INVALID_MOVE] = {
    "title": SHOW_GAME_TITLE,
    "pattern": r"Move not allowed|Movimiento no permitido"
}


class AdditionalMoveTest(tests.BaseModelTest):
    def setUp(self):
        super().setUp()
        self.game = Game.objects.create(
                                        cat_user=self.users[0],
                                        mouse_user=self.users[1],
                                        status=GameStatus.ACTIVE)

    def test1(self):
        ''' main author: Rafael Sanchez '''
        """ Movimiento de un ratón desde posiciones en la que no está """
        moves = [
            {"origin": 61, "target": 52},
            {"origin": 57, "target": 50},
        ]
        Move.objects.create(game=self.game, player=self.game.cat_user,
                            origin=0, target=9)
        for move in moves:
            with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
                Move.objects.create(
                                    game=self.game,
                                    player=self.game.mouse_user,
                                    origin=move["origin"],
                                    target=move["target"])
            self.assertEqual(self.game.moves.count(), 1)

    def test2(self):
        ''' main author: Alejandro Santorum '''
        """ Conversiones a string """
        move = Move(
                    game=self.game,
                    player=self.game.cat_user,
                    origin=0,
                    target=9)
        self.assertEqual(str(move), "[cat_user_test] - Origen: 0 - Destino: 9")
