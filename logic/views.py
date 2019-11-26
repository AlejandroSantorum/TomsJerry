from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from logic.forms import UserForm, SignupForm, MoveForm
from datamodel import constants
from datamodel.models import Counter, Game, GameStatus, Move
from django.db.models import Q


def anonymous_required(f):
    """
    anonymous_required (main author: Rafael Sanchez)
    ----------
    Input parameters:
        f: decorated function
    ----------
    Returns:
        function wrapped
    ----------
    Raises:
        None
    ----------
    Description:
        Decorator definition. It  implements a filterthat redirects to a error
        page in case the function that it 'decorates' is invoked by an
        authenticated user.
    """
    def wrapped(request):
        if request.user.is_authenticated:
            return HttpResponseForbidden(
                errorHTTP(request,
                          exception="Action restricted to anonymous users"))
        else:
            return f(request)
    return wrapped


def errorHTTP(request, exception=None):
    """
    errorHTTP (main author: Rafael Sanchez)
    ----------
    Input parameters:
        request: received request
        exception: error message ID. None by default.
    ----------
    Returns:
        It renders "mouse_cat/error.html" template
    ----------
    Raises:
        None
    ----------
    Description:
        It renders "mouse_cat/error.html" template with the error message.
    """
    context_dict = {}
    context_dict[constants.ERROR_MESSAGE_ID] = exception
    return render(request, "mouse_cat/error.html", context_dict)


def index(request):
    """
    index (main author: Alejandro Santorum)
    ----------
    Input parameters:
        request: received request
    ----------
    Returns:
        It renders "mouse_cat/index.html" template
    ----------
    Raises:
        None
    ----------
    Description:
        It renders "mouse_cat/index.html" template.
    """
    return render(request, "mouse_cat/index.html")


@anonymous_required
def user_login(request):
    """
    user_login (main author: Alejandro Santorum)
    ----------
    Input parameters:
        request: received request. In its body receives two strings, username
            and the user password
    ----------
    Returns:
        It renders "mouse_cat/index.html" template or "mouse_cat/login.html"
    ----------
    Raises:
        None
    ----------
    Description:
            Case method 'POST': It renders "mouse_cat/index.html" template in
            case the user is logged successfully. Otherwise it renders
        "mouse_cat/login.html" again.
            Case method 'GET': It renders "mouse_cat/login.html" with the user
        form data.
            It both cases the user is required to be anonymous, i.e, not logged
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next = request.POST.get('return_service')
        user_form = UserForm(data=request.POST)
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            request.session[constants.COUNTER_SESSION_ID] = 0
            if next != 'None' and next is not None:
                return redirect(next)
            return render(request, "mouse_cat/index.html")
        else:
            user_form.errors['username'] = []
            user_form.add_error('username', 'Username/password is not valid')
            context_dict = {'user_form': user_form, 'return_service': next}
            return render(request, "mouse_cat/login.html", context_dict)

    user_form = UserForm()
    context_dict = {'user_form': user_form,
                    'return_service': request.GET.get('next')}
    return render(request, "mouse_cat/login.html", context_dict)


def user_logout(request):
    """
    user_logout (main author: Alejandro Santorum)
    ----------
    Input parameters:
        request: received request. In its body receives nothing
    ----------
    Returns:
        It renders "mouse_cat/logout.html"
    ----------
    Raises:
        None
    ----------
    Description:
            It deletes counter session ID and game selected ID from session
        info; then the user is logged out. Finally, it's rendered the
        "mouse_cat/logout.html" template.
            It both cases the user is required to be logged.
    """
    if not request.user.is_authenticated:
        return redirect(reverse('index'))

    context_dict = {'user': request.user.username}
    request.session.pop(constants.COUNTER_SESSION_ID, None)
    request.session.pop(constants.GAME_SELECTED_SESSION_ID, None)
    logout(request)
    return render(request, "mouse_cat/logout.html", context_dict)


@anonymous_required
def signup(request):
    """
    signup (main author: Rafael Sanchez)
    ----------
    Input parameters:
        request: received request. In its body receives two strings, username
            and the user password
    ----------
    Returns:
        It renders "mouse_cat/signup.html" template
    ----------
    Raises:
        None
    ----------
    Description:
            Case method 'POST': If the fields validation is good, it creates a
        new user and it is autheticated in the application.
            Case method 'GET': It renders "mouse_cat/signup.html" in order to
        ahow signup form.
            It both cases the user is required to be anonymous, i.e, not logged
    """
    if request.method == 'POST':
        user_form = SignupForm(data=request.POST)
        if user_form.is_valid():
            cd = user_form.cleaned_data
        else:
            return render(request, "mouse_cat/signup.html",
                          {'user_form': user_form})

        if cd['password'] != cd['password2']:
            user_form.add_error(
                                'password2',
                                'Password and Repeat password are not the same'
                               )
            return render(
                          request,
                          "mouse_cat/signup.html",
                          {'user_form': user_form}
                         )

        try:
            validate_password(cd['password'])
        except ValidationError as err:
            user_form.errors['password'] = err.messages
            # user_form.add_error('password', ' '.join(err.messages))
            return render(
                          request,
                          "mouse_cat/signup.html",
                          {'user_form': user_form}
                         )

        # try:
        user = user_form.save()
        user.set_password(user.password)
        user.save()
        login(request, user)
        return render(request, "mouse_cat/signup.html")

    context_dict = {'user_form': SignupForm()}
    return render(request, "mouse_cat/signup.html", context_dict)


def counter(request):
    """
    counter (main author: Alejandro Santorum)
    ----------
    Input parameters:
        request: received request. In its body receives nothing.
    ----------
    Returns:
        It renders "mouse_cat/counter.html" template
    ----------
    Raises:
        None
    ----------
    Description:
            It updates and shows several counters of the received requests
    """
    Counter.objects.inc()
    counter_global = Counter.objects.get_current_value()

    if not request.session.get(constants.COUNTER_SESSION_ID):
        request.session[constants.COUNTER_SESSION_ID] = 1
        counter_session = 1
    else:
        request.session[constants.COUNTER_SESSION_ID] += 1
        counter_session = request.session[constants.COUNTER_SESSION_ID]

    context_dict = {'counter_session': counter_session,
                    'counter_global': counter_global}
    return render(request, "mouse_cat/counter.html", context_dict)


@login_required
def create_game(request):
    """
    create_game (main author: Rafael Sanchez)
    ----------
    Input parameters:
        request: received request. It contains logged user information.
    ----------
    Returns:
        It renders "mouse_cat/new_game.html" template
    ----------
    Raises:
        None
    ----------
    Description:
        It creates a game. Caller user (player 1) is the game owner and it
        waits for player 2 to join.
        It both cases the user is required to be logged.
    """
    game = Game.objects.create(cat_user=request.user)
    return render(request, "mouse_cat/new_game.html", {'game': game})


@login_required
def join_game(request):
    """
    join_game (main author: Rafael Sanchez)
    ----------
    Input parameters:
        request: received request. It contains logged user information.
    ----------
    Returns:
        It renders "mouse_cat/join_game.html" template
    ----------
    Raises:
        None
    ----------
    Description:
        The selected game is activated and it's the player 1 turn.
        It both cases the user is required to be logged.
    """
    pending_games = Game.objects.filter(mouse_user=None)
    pending_games = pending_games.exclude(cat_user=request.user)
    pending_games = pending_games.order_by('-id')
    if len(pending_games) == 0:
        context_dict = {constants.ERROR_MESSAGE_ID:
                        'There is no available games'}
        return render(request, "mouse_cat/join_game.html", context_dict)
    game = pending_games[0]
    game.mouse_user = request.user
    game.save()
    return render(request, "mouse_cat/join_game.html", {'game': game})


@login_required
def select_game(request, game_id=None):
    """
    select_game (main author: Alejandro Santorum)
    ----------
    Input parameters:
        method 'GET': received request. It contains logged user information.
        method 'POST': received request and the game ID to be played.
    ----------
    Returns:
        It renders "mouse_cat/select_game.html" template
        "mouse_cat/show_game.html"
    ----------
    Raises:
        None
    ----------
    Description:
            Once one game is selected (from the list of available games). its
        ID is stored into a variable called 'game_selected'
            It both cases the user is required to be logged.
    """
    if game_id:
        my_games = Game.objects.filter(Q(cat_user=request.user) |
                                       Q(mouse_user=request.user))
        my_games = list(my_games.filter(status=GameStatus.ACTIVE))
        my_games = [game.id for game in my_games]
        if game_id in my_games:
            request.session[constants.GAME_SELECTED_SESSION_ID] = int(game_id)
            return redirect(reverse('show_game'))
        else:
            return HttpResponse('Selected game does not exist.', status=404)
    # GET
    as_cat = list(Game.objects.filter(cat_user=request.user,
                                      status=GameStatus.ACTIVE))
    as_mouse = list(Game.objects.filter(mouse_user=request.user,
                                        status=GameStatus.ACTIVE))
    context_dict = {'as_cat': as_cat, 'as_mouse': as_mouse}
    return render(request, "mouse_cat/select_game.html", context_dict)


@login_required
def show_game(request):
    """
    show_game (main author: Rafael Sanchez)
    ----------
    Input parameters:
        request: received request. It also contains player and
            selected game information.
    ----------
    Returns:
            It renders "mouse_cat/game.html" template or
        "mouse_cat/select_game.html" template if there is no selected game
    ----------
    Raises:
        None
    ----------
    Description:
            It shows the selected game data, including the game board,
        represented as an integer array [0,63]. Cats are represented with
        value 1 and mouse with value -1.
            User is required to be logged.
    """
    if not request.session.get(constants.GAME_SELECTED_SESSION_ID):
        return redirect(reverse('select_game'))

    try:
        game_id = request.session.get(constants.GAME_SELECTED_SESSION_ID)
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return redirect(reverse('select_game'))

    board = [0]*constants.BOARD_SIZE
    board[game.mouse] = -1
    for i in game._get_cat_places():
        board[i] = 1
    context_dict = {'board': board, 'game': game, 'move_form': MoveForm()}
    return render(request, "mouse_cat/game.html", context_dict)


@login_required
def move(request):
    """
    move (main author: Alejandro Santorum)
    ----------
    Input parameters:
        request: received request. It also contains player, selected game
            information and origin and target of the movement. Player and
            game information are included in session variable. Origin and
            target can be found at the POST body parameters.
    ----------
    Returns:
        It renders "mouse_cat/show_game.html" template; or Error 404 if an
        invalid method is used.
    ----------
    Raises:
        None
    ----------
    Description:
        It develops a movement of a given player in the selected game.
        User is required to be logged.
    """
    if request.method == 'GET':
        return HttpResponse('Invalid method.', status=404)
    # POST
    if not request.session.get(constants.GAME_SELECTED_SESSION_ID):
        return HttpResponse('Invalid method.', status=404)
    game_id = request.session.get(constants.GAME_SELECTED_SESSION_ID)
    game = Game.objects.get(id=game_id)

    origin = int(request.POST.get('origin'))
    target = int(request.POST.get('target'))
    move_form = MoveForm(data=request.POST)
    move = Move(origin=origin, target=target, game=game, player=request.user)
    try:
        move.save()
    except ValidationError as err:
        move_form.add_error('origin', err.messages[0])
        board = [0]*constants.BOARD_SIZE
        board[game.mouse] = -1
        for i in game._get_cat_places():
            board[i] = 1
        context_dict = {'board': board, 'game': game, 'move_form': move_form}
        return render(request, "mouse_cat/game.html", context_dict)
    return redirect(reverse('show_game'))
