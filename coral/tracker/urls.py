from django.conf.urls.defaults import *

from models import Issue
import settings
import views

# Generic list_detail views
urlpatterns = patterns('django.views.generic',
	
	url(r'^$', views.issue_list, {'extra_context': {'tab': 'issues'}, 'paginate_by': settings.ISSUES_PER_PAGE}, name='tracker_issues'),
	
	url(r'^(?P<object_id>\d+)/$', 'list_detail.object_detail', {'queryset': Issue.objects.all(), 'extra_context': {'tab': 'issues'}}, name='tracker_issue_detail'),
	url(r'^(?P<object_id>\d+)/delete/$', 'create_update.delete_object', {'model': Issue, 'post_delete_redirect': '/issues/', 'extra_context': {'tab': 'issues'}}, name='tracker_delete_issue'),
	
)

urlpatterns += patterns('',

	url(r'^new/$', views.create_issue, {'extra_context': {'tab': 'issues'}}, name='tracker_create_issue'),
	url(r'^(?P<issue_id>\d+)/edit/$', views.update_issue, {'extra_context': {'tab': 'issues'}}, name='tracker_update_issue'),
	url(r'^(?P<issue_id>\d+)/add_note/$', views.add_note, {'extra_context': {'tab': 'issues'}}, name='tracker_add_note'),
	
	url(r'^tagged/(?P<tag>.+)/$', views.issue_list, {'extra_context': {'tab': 'issues'}}, name='tracker_issues_by_tag'),
	#url(r'^tagged/(?P<tag>.+)/$',tagged_object_list, {'template_name': 'tracker/issue_list.html', 'queryset_or_model': Issue, 'extra_context': {'tab': 'issues'}}, name='tracker_issues_by_tag'),
	
	url(r'^api/$', views.api, name='tracker_api'),

)
