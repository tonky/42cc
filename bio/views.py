# Create your views here.
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import RequestContext
from bio.models import Bio
from django.forms import ModelForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


class BioForm(ModelForm):

    class Meta:
        model = Bio


def index(request):
    bio = Bio.objects.get(pk=1)
    return render_to_response('index.html', {'bio': bio},
                              context_instance=RequestContext(request))


@login_required(redirect_field_name='/')
def edit(request):
    bio = Bio.objects.get(pk=1)

    form = BioForm(instance=bio)

    return render_to_response('edit_form.html', {'form': form},
                              context_instance=RequestContext(request))


def logoff(request):
    logout(request)
    return HttpResponseRedirect('/')


def save(request):
    bio = Bio.objects.get(pk=1)
    form = BioForm(request.POST, instance=bio)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect('/')

    form = BioForm(request.POST)

    return render_to_response('edit_form.html', {'form': form},
                              context_instance=RequestContext(request))
