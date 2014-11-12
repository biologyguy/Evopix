# - * - Coding: utf -8 - * -
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from evp.models import *
from resources.Evo import Evopic
from resources import mutation, breed
import re


# Create your views here.
def index(request):
    return render(request, 'templates/index.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:  # `NONE` is returned if a user isn't found
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/farm')
            else:  # Account is inactive
                return HttpResponse("Your Evopix account is disabled.")
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    else:
        print("Why not POST?")
        return render(request, 'templates/index.html')


def user_logout(request):
    #Handle the user's desire to log out
    x = 1


def not_found(request):
    if request.method == "POST":
        evp = request.POST.get('evp', '')
        bob = Evopic(evp)
        output = {"svg": bob.svg_out(bounding_box=(325, 325)), "evp": bob.evp}
        for i in range(1, 9):
            baby = mutation.mutate(Evopic(evp))

            output["svg%s" % i] = baby.svg_out(bounding_box=(180, 180))
            output["evp%s" % i] = baby.evp

        return render(request, 'templates/404.html', output)

    else:
        bob = Evopic(Evopix.objects.all()[1].evp)
        return render(request, 'templates/404.html', {"svg": bob.svg_out(bounding_box=(325, 325)), "evp": bob.evp})


#-------------------------Sandbox-------------------------------#
def run():
    print("Hello there")