# Create your views here.
import json
import time
from django.http import HttpResponse
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import RequestContext
from bio.models import Bio
from django.forms import ModelForm
from django.forms.widgets import DateInput
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


class ReadOnlyDate(DateInput):

    def render(self, name, value, attrs=None):
        attrs.update({"readonly": "readonly", "size": "8"})

        return super(ReadOnlyDate, self).render(name, value, attrs)


class BioForm(ModelForm):

    class Meta:
        model = Bio
        fields = list(reversed([field.name for field in Bio._meta.fields]))
        widgets = {
            'born': ReadOnlyDate(),
        }


def index(request):
    bio = Bio.objects.get(pk=1)
    return render_to_response('index.html', {'bio': bio, 'request': request},
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


def save_ajax(request):
    time.sleep(0.3)  # latency imitation, also needed for FF tests
    bio = Bio.objects.get(pk=1)
    form = BioForm(request.POST, instance=bio)

    if form.is_valid():
        form.save()
        return HttpResponse(json.dumps({'status': 0}))

    form = BioForm(request.POST)

    return HttpResponse(json.dumps({'status': 1, 'errors': form.errors}))
