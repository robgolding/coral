from django.conf.urls.defaults import *

from models import Issue
import settings
import views

# Generic list_detail views
urlpatterns = patterns('django.views.generic',
	
	url(r'^$', views.issue_list, {'extra_context': {'tab': 'issues'}, 'paginate_by': settings.ISSUES_PER_PAGE}, name='tracker_issues'),
	
	url(r'^(?P<object_id>\d+)/$', 'list_detail.object_detail', {'queryset': Issue.objects.all(), 'extra_context': {'tab': 'issues'}}, name='tracker_issue_detail'),
	
	url(r'^(?P<object_id>\d+)/summary/$', views.issue_summary, {'queryset': Issue.objects.all(), 'template_name': 'tracker/issue_summary_inner.html'}, name='tracker_issue_summary'),
	
	url(r'^(?P<issue_id>\d+)/edit/$', views.update_issue, {'extra_context': {'tab': 'issues'}}, name='tracker_update_issue'),
	
	url(r'^(?P<issue_id>\d+)/add_note/$', views.add_note, {'extra_context': {'tab': 'issues'}}, name='tracker_add_note'),
	
	url(r'^(?P<object_id>\d+)/star_unstar/$', views.star_unstar, {}, name='tracker_star_unstar'),
	
	url(r'^(?P<object_id>\d+)/delete/$', 'create_update.delete_object', {'model': Issue, 'post_delete_redirect': '/issues/', 'extra_context': {'tab': 'issues'}}, name='tracker_delete_issue'),
	
	url(r'^new/$', views.create_issue, {'extra_context': {'tab': 'issues'}}, name='tracker_create_issue'),
	
	url(r'^tagged/(?P<tag>.+)/$', views.issue_list, {'extra_context': {'tab': 'issues'}}, name='tracker_issues_by_tag'),
	
)
