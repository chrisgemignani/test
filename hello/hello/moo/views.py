# Create your views here.

from django.http import HttpResponse



def gotit(request):
    return HttpResponse("got it baby")
