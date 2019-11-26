from django import forms
from django.contrib.auth.models import User
from datamodel.models import Move, Game
from django.core.validators import MaxValueValidator, MinValueValidator


class UserForm(forms.ModelForm):
    """
    UserForm  (main author: Alejandro Santorum)
    ----------
    Description:
        It defines the log in form, in order to get username and password
    """
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password')


class SignupForm(forms.ModelForm):
    """
    SignupForm (main author: Rafael Sanchez)
    ----------
    Description:
        It defines the sign up form, in order to get username and
        password (twice to avoid missclicks)
    """
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password')


class MoveForm(forms.ModelForm):
    """
    MoveForm (main author: Alejandro Santorum)
    ----------
    Description:
        It defines the movement form, in order to get the orgin and the target
    """
    origin = forms.IntegerField(validators=[
                                            MaxValueValidator(Game.MAX_CELL),
                                            MinValueValidator(Game.MIN_CELL)
                                          ])
    target = forms.IntegerField(validators=[
                                            MaxValueValidator(Game.MAX_CELL),
                                            MinValueValidator(Game.MIN_CELL)
                                          ])

    class Meta:
        model = Move
        fields = ('origin', 'target')
