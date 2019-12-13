"""
"""

from django.core.exceptions import ValidationError
from django.urls import reverse

from datamodel import tests
from datamodel.models import Game, GameStatus, Move, Counter
from decimal import Decimal
import json
import re
from . import tests_services
from logic.tests_services import BaseModelTest as BMTest
from . import forms

GAME_STATUS_SERVICE = "game_status"
GET_MOVE_SERVICE = "get_move"


class AdditionalMoveTest(tests.BaseModelTest):
    def setUp(self):
        super().setUp()
        self.game = Game.objects.create(cat_user=self.users[0],
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
                Move.objects.create(game=self.game,
                                    player=self.game.mouse_user,
                                    origin=move["origin"],
                                    target=move["target"])
            self.assertEqual(self.game.moves.count(), 1)

    def test2(self):
        ''' main author: Alejandro Santorum '''
        """ Conversiones a string """
        move = Move(game=self.game,
                    player=self.game.cat_user,
                    origin=0,
                    target=9)
        self.assertEqual(str(move), "[cat_user_test] - Origen: 0 - Destino: 9")


class AdditionalGameTest(tests.BaseModelTest):
    def setUp(self):
        super().setUp()
        self.game = Game.objects.create(cat_user=self.users[0],
                                        mouse_user=self.users[1],
                                        status=GameStatus.ACTIVE)

    def test1(self):
        ''' main author: Rafael Sanchez '''
        """ Guarda una partida finalizada que pierde el raton """

        self.game.cat1 = 0
        self.game.cat2 = 2
        self.game.cat3 = 16
        self.game.cat4 = 18
        self.game.mouse = 9

        self.game.save()
        self.assertEqual(self.game.status, GameStatus.FINISHED)


class GameStatusService(tests_services.PlayGameBaseServiceTests):
    def setUp(self):
        super().setUp()

        self.game = Game.objects.create(cat_user=self.user1,
                                        mouse_user=self.user2,
                                        status=GameStatus.ACTIVE)
        self.moves = [
            {"player": self.user1, "origin": 0, "target": 9},
            {"player": self.user2, "origin": 59, "target": 50},
            {"player": self.user1, "origin": 2, "target": 11},
        ]

        for move in self.moves:
            Move.objects.create(game=self.game,
                                player=move["player"],
                                origin=move["origin"],
                                target=move["target"])

        self.game.status = GameStatus.FINISHED
        self.game.save()

    def tearDown(self):
        super().tearDown()

    def test1(self):
        """ Petición al ENDPOINT /game_status con ganador """
        self.game.winner = self.user1
        self.game.save()
        self.set_game_in_session(self.client1, self.user1, self.game.id)
        response = self.client.get(reverse(GAME_STATUS_SERVICE), follow=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(self.decode(response.content))
        self.assertEqual(data['status'], self.game.status)
        self.assertEqual(data['winner'], self.game.winner.username)

    def test2(self):
        """ Petición al ENDPOINT /game_status sin ganador """
        self.set_game_in_session(self.client1, self.user1, self.game.id)
        response = self.client.get(reverse(GAME_STATUS_SERVICE), follow=True)
        self.assertEqual(response.status_code, 200)
        data = json.loads(self.decode(response.content))
        self.assertEqual(data['status'], self.game.status)
        self.assertEqual(data['winner'], None)


class AdditionalGetMoveServiceTests(tests_services.PlayGameBaseServiceTests):
    def setUp(self):
        super().setUp()

        self.game = Game.objects.create(cat_user=self.user1,
                                        mouse_user=self.user2,
                                        status=GameStatus.ACTIVE)
        self.moves = [
            {"player": self.user1, "origin": 0, "target": 9},
            {"player": self.user2, "origin": 59, "target": 50},
            {"player": self.user1, "origin": 2, "target": 11},
        ]

        for move in self.moves:
            Move.objects.create(game=self.game,
                                player=move["player"],
                                origin=move["origin"],
                                target=move["target"])
        self.game.status = GameStatus.FINISHED
        self.game.save()

    def tearDown(self):
        super().tearDown()

    def test1(self):
        """ No game selected """
        self.set_game_in_session(self.client1, self.user1, None)
        response = self.client1.post(reverse(GET_MOVE_SERVICE), {"shift": 1},
                                     follow=True,
                                     HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)


class MoveServiceTests(tests_services.PlayGameBaseServiceTests):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test1(self):
        """ Campos de formulario válidos """
        self.assertTrue(forms.MoveForm({"origin": 0,
                                        "target": 0}).is_valid())
        self.assertFalse(forms.MoveForm({"origin": -1,
                                         "target": 0}).is_valid())
        self.assertFalse(forms.MoveForm({"origin": 64,
                                         "target": 0}).is_valid())
        self.assertFalse(forms.MoveForm({"origin": 0,
                                         "target": -1}).is_valid())
        self.assertFalse(forms.MoveForm({"origin": 0,
                                         "target": 64}).is_valid())

    def test2(self):
        """ GET no permitido """
        game = Game.objects.create(cat_user=self.user1, mouse_user=self.user2,
                                   status=GameStatus.ACTIVE)
        self.set_game_in_session(self.client1, self.user1, game.id)
        ms = tests_services.MOVE_SERVICE
        response = self.client.get(reverse(ms), follow=True)
        self.assertEqual(response.status_code, 404)

    def test3(self):
        """ Secuencia de movimientos válidos """
        moves = [
            {**self.sessions[0], **{"origin": 0, "target": 9,
                                    "positions": [9, 2, 4, 6, 59]}},
            {**self.sessions[1], **{"origin": 59, "target": 50,
                                    "positions": [9, 2, 4, 6, 50]}},
            {**self.sessions[0], **{"origin": 9, "target": 16,
                                    "positions": [16, 2, 4, 6, 50]}},
            {**self.sessions[1], **{"origin": 50, "target": 41,
                                    "positions": [16, 2, 4, 6, 41]}},
        ]

        game_t0 = Game.objects.create(cat_user=self.user1,
                                      mouse_user=self.user2,
                                      status=GameStatus.ACTIVE)

        for session in self.sessions:
            self.set_game_in_session(session["client"], session["player"],
                                     game_t0.id)

        n_moves = 0
        for move in moves:
            ms = tests_services.MOVE_SERVICE
            response = move["client"].post(reverse(ms), move, follow=True)
            self.assertEqual(response.status_code, 200)

            game_t1 = Game.objects.get(id=game_t0.id)
            n_moves += 1
            self.assertNotEqual(str(game_t0), str(game_t1))
            self.assertEqual(BMTest.get_array_positions(game_t1),
                             move["positions"])
            self.assertEqual(game_t1.cat_turn, move["player"] == self.user2)
            self.assertEqual(game_t1.moves.count(), n_moves)

            game_t0 = game_t1

    def test4(self):
        """ Llamada a mover si no existe un juego seleccionado """
        moves = [
            {**self.sessions[0], **{"origin": 0, "target": 9}},
            {**self.sessions[1], **{"origin": 59, "target": 50}},
        ]

        game_t0 = Game.objects.create(cat_user=self.user1,
                                      mouse_user=self.user2,
                                      status=GameStatus.ACTIVE)
        for session in self.sessions:
            self.loginTestUser(session["client"], session["player"])

        for move in moves:
            ms = tests_services.MOVE_SERVICE
            response = move["client"].post(reverse(ms), move, follow=True)
            self.assertEqual(response.status_code, 404)
            game_t1 = Game.objects.get(id=game_t0.id)
            self.assertEqual(str(game_t0), str(game_t1))
            self.assertEqual(game_t1.moves.count(), 0)

            game_t0.cat_turn = not game_t1.cat_turn
            game_t0.save()

    def test5(self):
        """ Movimientos inválido """
        moves = [
            {**self.sessions[0], **{"origin": 1, "target": 9,
                                    "positions": [9, 2, 4, 6, 59]}},
            {**self.sessions[1], **{"origin": 58, "target": 50,
                                    "positions": [9, 2, 4, 6, 50]}},
            {**self.sessions[0], **{"origin": 9, "target": 16,
                                    "positions": [16, 2, 4, 6, 50]}},
            {**self.sessions[1], **{"origin": 50, "target": 41,
                                    "positions": [16, 2, 4, 6, 41]}},
        ]

        game_t0 = Game.objects.create(cat_user=self.user1,
                                      mouse_user=self.user2,
                                      status=GameStatus.ACTIVE)
        for session in self.sessions:
            self.set_game_in_session(session["client"],
                                     session["player"],
                                     game_t0.id)

        n_moves = 0
        ms = tests_services.MOVE_SERVICE
        for move in moves:
            response = move["client"].post(reverse(ms), move, follow=True)
            self.assertEqual(response.status_code, 200)

            game_t1 = Game.objects.get(id=game_t0.id)
            self.assertEqual(str(game_t0), str(game_t1))
            self.assertNotEqual(BMTest.get_array_positions(game_t1),
                                move["positions"])
            self.assertEqual(game_t1.moves.count(), n_moves)

            game_t0 = game_t1


class SelectGameServiceTests(tests_services.GameRequiredBaseServiceTests):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test1(self):
        """ Validación del listado de juegos que puedo seleccionar como gato
            y como ratón en play game """
        as_cat1 = []
        as_cat2 = []
        as_cat = []
        as_mouse = []

        for _ in range(1, 8):
            as_cat1.append(Game.objects.create(cat_user=self.user1))

        for _ in range(1, 8):
            as_cat2.append(Game.objects.create(cat_user=self.user2))

        n_actives = 0
        for game in filter(lambda game: game.id % 2, as_cat1):
            game.mouse_user = self.user2
            if n_actives <= 2:
                game.status = GameStatus.ACTIVE
                as_mouse.append(game)
                n_actives += 1
            else:
                GameStatus.FINISHED
            game.save()

        n_actives = 0
        for game in filter(lambda game: game.id % 2 != 0, as_cat2):
            game.mouse_user = self.user1
            if n_actives <= 2:
                game.status = GameStatus.ACTIVE
                as_cat.append(game)
                n_actives += 1
            else:
                GameStatus.FINISHED
            game.save()

        self.loginTestUser(self.client2, self.user2)
        sgm = tests_services.SELECT_GAME_SERVICE
        response = self.client2.get(reverse(sgm,
                                            args=['play_game']), follow=True)
        for game in as_cat + as_mouse:
            self.assertIn('Game: '+str(game.id), self.decode(response.content))

    def test2(self):
        """ Validación del listado de juegos a seleccionar en join_game """
        as_cat1 = []

        for _ in range(1, 8):
            as_cat1.append(Game.objects.create(cat_user=self.user1))

        self.loginTestUser(self.client2, self.user2)
        response = self.client2.get(reverse(tests_services.SELECT_GAME_SERVICE,
                                            args=['join_game']), follow=True)
        for game in as_cat1:
            self.assertIn('Game: '+str(game.id), self.decode(response.content))

    def test3(self):
        """ Validación del listado de juegos a seleccionar en replay_game """
        games = []

        for _ in range(1, 8):
            games.append(Game.objects.create(cat_user=self.user1,
                                             mouse_user=self.user2,
                                             status=GameStatus.FINISHED))

        self.loginTestUser(self.client2, self.user2)
        response = self.client2.get(reverse(tests_services.SELECT_GAME_SERVICE,
                                            args=['replay_game']), follow=True)
        for game in games:
            self.assertIn('Game: '+str(game.id), self.decode(response.content))


class CounterServiceTests(tests_services.ServiceBaseTest):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def is_counter_session(self, response, value):
        m = re.search(r"Counter session: <b>(?P<session_counter>\d+)</b>",
                      self.decode(response.content))
        self.assertEqual(Decimal(m.group("session_counter")), value)

    def is_counter_global(self, response, value):
        m = re.search(r"Counter global: <b>(?P<global_counter>\d+)</b>",
                      self.decode(response.content))
        self.assertEqual(Decimal(m.group("global_counter")), value)

    def test1(self):
        """ Actualización correcta del contador de sesión """
        cgs = tests_services.CREATE_GAME_SERVICE
        cs = tests_services.COUNTER_SERVICE
        for i in range(1, 4):
            self.client1.get(reverse(cgs), follow=True)
            response = self.client1.get(reverse(cs), follow=True)
            self.is_counter_session(response, i)
        for i in range(1, 3):
            self.client2.get(reverse(cgs), follow=True)
            response = self.client2.get(reverse(cs), follow=True)
            self.is_counter_session(response, i)
        for i in range(4, 6):
            self.client1.get(reverse(cgs), follow=True)
            response = self.client1.get(reverse(cs), follow=True)
            self.is_counter_session(response, i)

    def test2(self):
        """ Actualización correcta del contador global """
        cgs = tests_services.CREATE_GAME_SERVICE
        cs = tests_services.COUNTER_SERVICE
        n_calls = Counter.objects.get_current_value()

        for _ in range(2):
            self.client1.get(reverse(cgs), follow=True)
            response = self.client1.get(reverse(cs), follow=True)
            n_calls += 1
            self.is_counter_global(response, n_calls)

            self.client1.get(reverse(cgs), follow=True)
            response = self.client2.get(reverse(cs), follow=True)
            n_calls += 1
            self.is_counter_global(response, n_calls)


class GameEndTests(tests.BaseModelTest):
    def setUp(self):
        super().setUp()
        self.game = Game.objects.create(cat_user=self.users[0],
                                        mouse_user=self.users[1],
                                        status=GameStatus.ACTIVE)
        self.game.cat1 = 4
        self.game.cat2 = 9
        self.game.cat3 = 25
        self.game.cat4 = 27
        self.game.mouse = 18
        self.game.save()

    def test1(self):
        ''' main author: Rafael Sanchez '''
        """ The cat makes the mouse unavailable to move """
        self.game.cat_turn = True
        self.game.save()

        Move.objects.create(game=self.game, player=self.game.cat_user,
                            origin=4, target=11)

        self.assertEqual(self.game.status, GameStatus.FINISHED)
        self.assertEqual(self.game.winner, self.game.cat_user)

    def test2(self):
        ''' main author: Alejandro Santorum '''
        """ The mouse escapes """
        self.game.cat_turn = False
        self.game.mouse = 11
        self.game.save()

        Move.objects.create(game=self.game, player=self.game.mouse_user,
                            origin=11, target=2)

        self.assertEqual(self.game.status, GameStatus.FINISHED)
        self.assertEqual(self.game.winner, self.game.mouse_user)

    def test3(self):
        ''' main author: Rafael Sanchez '''
        """ The cat commits suicide """
        self.game.cat_turn = True
        self.game.mouse = 11
        self.game.save()

        Move.objects.create(game=self.game, player=self.game.cat_user,
                            origin=4, target=13)

        self.assertEqual(self.game.status, GameStatus.FINISHED)
        self.assertEqual(self.game.winner, self.game.mouse_user)
