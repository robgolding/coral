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

def svn_revision(request):
	import os
	if hasattr(django_settings, 'WORKING_COPY') and django_settings.WORKING_COPY:
		rev = "(working copy)"
	else:
		try:
			f = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'svn-revision'))
			rev = f.read()
			rev = 'svn-%s' % rev
		except IOError:
			rev = None
	return {'svn_revision': rev}
		
