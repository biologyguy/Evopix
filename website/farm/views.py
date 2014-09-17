from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
# Create your views here.


def farm(request, user_id):
    new_farm = Farm.objects.get(pk=user_id)
    render_to_response('farm/farm.html', {'farm':new_farm}, RequestContext(request))