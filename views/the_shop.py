from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from evp.models import *
from resources.Evo import Evopic
from resources import mutation, breed
import re
import traceback
from django.contrib.auth.decorators import login_required

@login_required
def store(request):
    if request.user.is_authenticated():
        user_id = request.user.id
    else:
        return HttpResponse("Something has gone wrong... Can't find your user name in farm view.")
    return render(request, 'templates/store.html', {"user_id": user_id})
