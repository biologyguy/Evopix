from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
# Create your views here.


def evopic(request, user_id):
    new_evopic = evopix.objects.get(pk=id)
    render_to_response('evopix/test_breed.html', {'evopix':new_evopic}, RequestContext(request))