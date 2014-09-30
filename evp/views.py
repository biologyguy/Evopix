from django.shortcuts import render
from evp.models import *


# Create your views here.
def welcome(self, request, *args, **kwargs):
    bob = Evopix.objects.all()[0]
    template_name = (bob.evo_id, bob.name)
    return render(request, template_name, context)