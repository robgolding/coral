# Context processors for the tracker application

import settings

from django.conf import settings as django_settings

def filter(request):
	extra_context = {}
	if request.GET.get('f'):
		extra_context.update({'filter': request.GET.get('f')})
	else:
		extra_context.update({'filter': settings.TRACKER_DEFAULT_FILTER})
	extra_context.update({'default_filter': settings.TRACKER_DEFAULT_FILTER})
	return extra_context
		
