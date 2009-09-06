from django.conf.urls.defaults import *

from django.contrib.auth.models import User

import profiles.views

# Generic list_detail views
urlpatterns = patterns('django.views.generic',
	
	url(r'^$', 'list_detail.object_list', {'queryset': User.objects.all(), 'template_name': 'users/user_list.html', 'extra_context': {'tab': 'users'}}, name='users_list'),
	
)


urlpatterns += patterns('',
	
	url(r'^(?P<username>.+)/$', profiles.views.profile_detail, {'template_name': 'users/user_detail.html', 'extra_context': {'tab': 'users'}}, name='users_user_detail'),
	
	url(r'^edit/(?P<username>.+)/$', profiles.views.edit_profile, {'template_name': 'users/edit_user.html', 'extra_context': {'tab': 'users'}}, name='users_edit_user'),
	
)
