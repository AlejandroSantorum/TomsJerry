from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime


MSG_ERROR_INVALID_CELL = "Invalid cell for a cat or the mouse|" +\
                         "Gato o ratón en posición no válida"
MSG_ERROR_GAMESTATUS = "Game status not valid|Estado no válido"
MSG_ERROR_MOVE = "Move not allowed|Movimiento no permitido"
MSG_ERROR_NEW_COUNTER = "Insert not allowed|Inseción no permitida"


class GameStatus():
    '''
    (main author: Alejandro Santorum)
    '''
    CREATED = 0
    ACTIVE = 1
    FINISHED = 2


class Game(models.Model):
    '''
    (main author: Rafael Sanchez)
    '''
    MIN_CELL = 0
    MAX_CELL = 63
    WIDTH = 8
    cat_user = models.ForeignKey(
                                 User,
                                 on_delete=models.CASCADE,
                                 related_name="games_as_cat")
    mouse_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,
                                   null=True, related_name="games_as_mouse")
    # Cat 1 position
    cat1 = models.IntegerField(validators=[
                                            MaxValueValidator(63),
                                            MinValueValidator(0)
                                          ],
                               default=0)  # Not NULL is set by default
    # Cat 2 position
    cat2 = models.IntegerField(validators=[
                                            MaxValueValidator(63),
                                            MinValueValidator(0)
                                          ],
                               default=2)
    # Cat 3 position
    cat3 = models.IntegerField(validators=[
                                            MaxValueValidator(63),
                                            MinValueValidator(0)
                                          ],
                               default=4)
    # Cat 4 position
    cat4 = models.IntegerField(validators=[
                                            MaxValueValidator(63),
                                            MinValueValidator(0)
                                          ],
                               default=6)
    # Mouse position
    mouse = models.IntegerField(default=59)
    # true if it's cat's turn, false if it's mouse turn
    cat_turn = models.BooleanField(default=True)
    # Game status
    status = models.IntegerField(default=GameStatus.CREATED)

    # Game moves
    @property
    def moves(self):
        return Move.objects.filter(game=self)

    def __str_game_status(self):
        if self.status == 0:
            return "Created"
        elif self.status == 1:
            return "Active"
        else:
            return "Finished"

    def __pos_is_valid(self, position):
        if not position:
            return True
        odd_col = bool((position//Game.WIDTH) % 2)
        odd_row = bool((position % Game.WIDTH) % 2)
        return not (odd_col ^ odd_row)

    def clean(self, exclude=None):
        # Validators for cat not null and cell's range are already
        # defined in model definition
        if self.status == GameStatus.CREATED and self.mouse_user is not None:
            raise ValidationError(MSG_ERROR_GAMESTATUS)
        if self.status == GameStatus.ACTIVE and not self.mouse_user:
            raise ValidationError(MSG_ERROR_GAMESTATUS)
        if self.status == GameStatus.FINISHED and not self.mouse_user:
            raise ValidationError(MSG_ERROR_GAMESTATUS)

    def save(self, *args, **kwargs):
        if self.mouse_user and self.status == GameStatus.CREATED:
            self.status = GameStatus.ACTIVE
        # Validations for test10 (valid cells) below:
        if not self.__pos_is_valid(self.cat1):
            raise ValidationError(MSG_ERROR_INVALID_CELL)
        if not self.__pos_is_valid(self.cat2):
            raise ValidationError(MSG_ERROR_INVALID_CELL)
        if not self.__pos_is_valid(self.cat3):
            raise ValidationError(MSG_ERROR_INVALID_CELL)
        if not self.__pos_is_valid(self.cat4):
            raise ValidationError(MSG_ERROR_INVALID_CELL)
        if not self.__pos_is_valid(self.mouse):
            raise ValidationError(MSG_ERROR_INVALID_CELL)
        super(Game, self).save(*args, **kwargs)

    def _get_cat_places(self):
        return [self.cat1, self.cat2, self.cat3, self.cat4]

    def __str__(self):
        id = str(self.id)
        status = self.__str_game_status()
        if self.cat_turn:
            c_turn = "[X]"
            m_turn = "[ ]"
        else:
            c_turn = "[ ]"
            m_turn = "[X]"

        c_pos = "(" + str(self.cat1) + ", " + str(self.cat2) + ", " +\
                str(self.cat3) + ", " + str(self.cat4) + ")"
        if not self.mouse_user:
            ret_str = "(" + id + ", " + status + ")\tCat " +\
                      c_turn + " " + str(self.cat_user) + c_pos
            return ret_str

        m_pos = "("+str(self.mouse)+")"
        ret_str = "(" + id + ", " + status + ")\tCat " + c_turn + " " +\
                  str(self.cat_user) + c_pos + " --- Mouse " + m_turn + " " +\
                  str(self.mouse_user) + m_pos
        return ret_str


class Move(models.Model):
    '''
    (main author: Alejandro Santorum)
    '''
    origin = models.IntegerField(validators=[
                                            MaxValueValidator(Game.MAX_CELL),
                                            MinValueValidator(Game.MIN_CELL)
                                          ])
    target = models.IntegerField(validators=[
                                            MaxValueValidator(Game.MAX_CELL),
                                            MinValueValidator(Game.MIN_CELL)
                                          ])
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)

    def __pos_to_list(self, position):
        return [(position//Game.WIDTH) + 1, (position % Game.WIDTH) + 1]

    def __cat_valid_move(self):
        if not self.game.cat_turn:
            return False
        cats = self.game._get_cat_places()
        if self.origin not in cats or self.target in cats:
            return False
        if self.target == self.game.mouse:
            return False
        origin_lst = self.__pos_to_list(self.origin)
        target_lst = self.__pos_to_list(self.target)
        SE_lst = [x+1 for x in origin_lst]
        SW_lst = [origin_lst[0]+1, origin_lst[1]-1]
        if SE_lst == target_lst:
            return True
        if SW_lst == target_lst:
            return True
        return False

    def __mouse_valid_move(self):
        if self.game.cat_turn:
            return False
        cats = self.game._get_cat_places()
        if self.target in cats:
            return False
        if self.origin != self.game.mouse:
            return False
        origin_lst = self.__pos_to_list(self.origin)
        target_lst = self.__pos_to_list(self.target)
        SE_lst = [x+1 for x in origin_lst]
        SW_lst = [origin_lst[0]+1, origin_lst[1]-1]
        NW_lst = [x-1 for x in origin_lst]
        NE_lst = [origin_lst[0]-1, origin_lst[1]+1]
        if SE_lst == target_lst:
            return True
        if SW_lst == target_lst:
            return True
        if NW_lst == target_lst:
            return True
        if NE_lst == target_lst:
            return True
        return False

    def save(self, *args, **kwargs):
        if self.target < 0 or self.target > 63:
            raise ValidationError(MSG_ERROR_MOVE)
        if self.player != self.game.mouse_user and\
           self.player != self.game.cat_user:
            raise ValidationError(MSG_ERROR_MOVE)
        if self.game.status != GameStatus.ACTIVE:
            raise ValidationError(MSG_ERROR_MOVE)
        if self.player == self.game.cat_user and not self.__cat_valid_move():
            raise ValidationError(MSG_ERROR_MOVE)
        if self.player == self.game.mouse_user and not\
           self.__mouse_valid_move():
            raise ValidationError(MSG_ERROR_MOVE)

        super(Move, self).save(*args, **kwargs)
        if self.player == self.game.mouse_user:
            self.game.mouse = self.target
            self.game.cat_turn = True
        else:
            if self.origin == self.game.cat1:
                self.game.cat1 = self.target
            elif self.origin == self.game.cat2:
                self.game.cat2 = self.target
            elif self.origin == self.game.cat3:
                self.game.cat3 = self.target
            else:
                self.game.cat4 = self.target
            self.game.cat_turn = False
        self.game.save()

    def __str__(self):
        return '['+str(self.player)+'] - Origen: '+str(self.origin)\
                + ' - Destino: '+str(self.target)


class CounterManager(models.Manager):
    '''
    (author: Rafael Sanchez)
    '''
    def init_counter(self):
        counter = Counter()
        super(Counter, counter).save()
        return counter

    def inc(self):
        objs = self.get_queryset()
        if len(objs) == 0:
            counter = self.init_counter()
        else:
            counter = objs[0]
        val = self.get_current_value()
        counter.value = val+1
        super(Counter, counter).save()
        return val+1

    def get_current_value(self):
        objs = super().get_queryset()
        if len(objs) == 0:
            return 0
        return objs[0].value


class Counter(models.Model):
    '''
    (author: Rafael Sanchez)
    '''
    value = models.IntegerField(default=0)
    objects = CounterManager()

    def save(self, *args, **kwargs):
        raise ValidationError(MSG_ERROR_NEW_COUNTER)
