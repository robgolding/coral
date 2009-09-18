from django.conf.urls.defaults import *
from django.contrib import admin
import settings

from tracker.utils import get_stats

from tracker.views import index

admin.autodiscover()

LOGOUT_REDIRECT_URL = getattr(settings, "LOGOUT_REDIRECT_URL", "/coral/")

urlpatterns = patterns('',
	
	url(r'^admin/(.*)', admin.site.root, name="admin"),
	
	url(r'^$', index, name="index"),
	(r'^issues/', include('coral.tracker.urls')),
	(r'^accounts/', include('coral.accounts.urls')),
	
	(r'^filter/', include('coral.filter.urls')),
	
	(r'^users/', include('coral.users.urls')),
	
	url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}, name="login"),
	
	url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': LOGOUT_REDIRECT_URL}, name="logout"),
	
)

if hasattr(settings, 'WORKING_COPY') and settings.WORKING_COPY:
	import os
	try:
		media_path = os.path.join(settings.PATH, 'media')
		urlpatterns += patterns('',
			(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': media_path}),
		)
	except NameError:
		raise ImproperlyConfigured, "You must define the PATH variable in your local_settings file."
