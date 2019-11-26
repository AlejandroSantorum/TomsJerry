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


class AdditionalShowGameServiceTest(PlayGameBaseServiceTests):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test1(self):
        ''' main author: Rafael Sanchez '''
        """ Vuelve al selector de juego si no hay un ID seleccionado """
        self.set_game_in_session(self.client1, self.user1, None)
        response = self.client1.get(reverse(SHOW_GAME_SERVICE), follow=True)
        self.is_select_game(response)

    def test2(self):
        ''' main author: Alejandro Santorum '''
        """ Vuelve al selector de juego si no hay para el ID seleccionado """
        self.set_game_in_session(self.client1, self.user1, 420)
        response = self.client1.get(reverse(SHOW_GAME_SERVICE), follow=True)
        self.is_select_game(response)


class AdditionalSignupServiceTest(ServiceBaseTest):
    def setUp(self):
        super().setUp()
        self.paramsUser1.update({"password2": self.paramsUser1["password"]})

    def tearDown(self):
        super().tearDown()

    def test1(self):
        ''' main author: Rafael Sanchez '''
        """ Carga del formulario de signup """
        self.assertFalse(self.client1.session.get(USER_SESSION_ID, False))
        response = self.client1.get(reverse(SIGNUP_SERVICE), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client1.session.get(USER_SESSION_ID, False))
        self.validate_response(SIGNUP_SERVICE, response)


class AdditionalLogInOutServiceTests(ServiceBaseTest):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test1(self):
        ''' main author: Alejandro Santorum '''
        """ Redirect al indice tras login """
        response = self.client1.get(reverse(SELECT_GAME_SERVICE), follow=True)
        self.is_login(response)
        response = self.client1.post(reverse(LOGIN_SERVICE), self.paramsUser1,
                                     follow=True)
        self.assertEqual(Decimal(self.client1.session.get(USER_SESSION_ID)),
                         self.user1.id)
        self.validate_response(INDEX_SERVICE, response)

    def test2(self):
        ''' main author: Rafael Sanchez '''
        """ Redirect a select game tras login """
        response = self.client1.get(reverse(SELECT_GAME_SERVICE), follow=True)
        self.is_login(response)
        next = response.redirect_chain[0][0]
        self.paramsUser1['return_service'] = next[next.find('=')+1:]
        response = self.client1.post(reverse(LOGIN_SERVICE), self.paramsUser1,
                                     follow=True)
        self.assertEqual(Decimal(self.client1.session.get(USER_SESSION_ID)),
                         self.user1.id)
        self.is_select_game(response)
        pass

    def test3(self):
        ''' main author: Alejandro Santorum '''
        """ Logout no hace nada con un usuario no registrado """
        self.assertFalse(self.client1.session.get(USER_SESSION_ID, False))
        response = self.client1.get(reverse(LOGOUT_SERVICE), follow=True)
        self.validate_response(INDEX_SERVICE, response)


class AdditionalMoveServiceTests(PlayGameBaseServiceTests):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test1(self):
        ''' main author: Rafael Sanchez '''
        """ Movimiento inválido """
        moves = [
            {**self.sessions[0], **{"origin": 0, "target": 10}},
            {**self.sessions[0], **{"origin": 1, "target": 9}},
            {**self.sessions[0], **{"origin": 1, "target": 10}}
        ]

        game_t0 = Game.objects.create(cat_user=self.user1,
                                      mouse_user=self.user2,
                                      status=GameStatus.ACTIVE)
        for session in self.sessions:
            self.set_game_in_session(session["client"],
                                     session["player"],
                                     game_t0.id)

        for move in moves:
            response = move["client"].post(reverse(MOVE_SERVICE),
                                           move,
                                           follow=True)
            self.assertEqual(response.status_code, 200)
            self.validate_response(PLAY_GAME_INVALID_MOVE, response)

            game_t1 = Game.objects.get(id=game_t0.id)
            self.assertEqual(str(game_t0), str(game_t1))
            game_t0 = game_t1
