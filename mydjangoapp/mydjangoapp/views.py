import os
import uuid
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.response import TemplateResponse
from rest_framework import mixins, viewsets

from .models import Job
from .serializers import JobSerializer
from .messagequeue import send_msg
from .redisconf import redis_conn


def home(request):
	context = {
		'user': request.user,
		'STATIC_URL': settings.STATIC_URL,
	}
	return TemplateResponse(request, 'home.html', context)



class JobViewSet(mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """
    API endpoint that allows jobs to be viewed or created.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer


@login_required
def get_ws_token(request):

	token = request.session.get('ws_token', None)
	if not token:
		token = uuid.uuid4().hex
		request.session['ws_token'] = token
		redis_conn.set(token, 1)

	send_msg({'token': token})
	return JsonResponse({'token': token})
