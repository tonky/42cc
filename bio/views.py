# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from bio.models import Bio


def index(request):
    bio = Bio.objects.get(pk=1)
    return render_to_response('index.html', {'bio': bio},
                              context_instance=RequestContext(request))
