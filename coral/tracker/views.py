from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list, object_detail
from django.core import serializers

from forms import NewIssueForm, EditIssueForm, AddNoteToIssueForm
from models import Issue, IssuePriority, Star
from tagging.models import TaggedItem
import settings

def index(request, extra_context={}, template_name='index.html'):
	data = {}
	if request.user.is_authenticated():
		assigned_issues = request.user.assigned.all()
		data['assigned_issues'] = assigned_issues
	data.update(extra_context)
	return render_to_response(template_name, data, context_instance=RequestContext(request))

def issue_list(request, tag=None, template_name='tracker/issue_list.html', **kwargs):
	if not kwargs.has_key('extra_context'):
		kwargs['extra_context'] = {}
	if tag is not None:
		kwargs['extra_context']['tag'] = tag
		queryset = TaggedItem.objects.get_by_model(Issue, tag)
	else:
		queryset = Issue.objects.all()
	filter = request.GET.get('f')
	if not filter: filter = settings.TRACKER_DEFAULT_FILTER
	if filter == 'closed':
		queryset = queryset.filter(status='closed')
	elif filter == 'open':
		queryset = queryset.exclude(status='closed')
	elif filter == 'all':
		pass
	kwargs['extra_context']['priorities'] = IssuePriority.objects.all()
	kwargs['extra_context']['filter'] = filter
	return object_list(request, queryset, template_name=template_name, **kwargs)

def issue_summary(request, object_id, queryset, *args, **kwargs):
	format = request.GET.get('format', 'html')
	if format == 'json':
		data = serializers.serialize("json", queryset.filter(pk=object_id))
		return HttpResponse(data, mimetype="application/javascript")
	elif format == 'xml':
		data = serializers.serialize("xml", queryset.filter(pk=object_id))
		return HttpResponse(data, mimetype="application/javascript")
	else:
		return object_detail(request, object_id=object_id, queryset=queryset, *args, **kwargs)

def star_unstar(request, object_id):
	issue = get_object_or_404(Issue, pk=object_id)
	star, created = Star.objects.get_or_create(user=request.user, issue=issue)
	if not created:
		star.delete()
	if request.is_ajax():
		data = {'object': issue}
		return render_to_response('tracker/issue_detail_star.html', data, context_instance=RequestContext(request))
	return HttpResponseRedirect(issue.get_absolute_url())

@login_required
def create_issue(request, extra_context={}, template='tracker/issue_form.html'):
	if request.method == 'POST':
		form = NewIssueForm(request.POST)
		if form.is_valid():
			issue = form.save(user=request.user)
			return HttpResponseRedirect(issue.get_absolute_url())
	else:
		form = NewIssueForm()
	data = { 'form': form, 'action': 'create' }
	data.update(extra_context)
	return render_to_response(template, data, context_instance=RequestContext(request))

@login_required
def update_issue(request, issue_id, extra_context={}, template='tracker/issue_form.html'):
	issue = get_object_or_404(Issue, id=issue_id)
	if request.method == 'POST':
		form = EditIssueForm(request.POST, instance=issue)
		if form.is_valid():
			issue = form.save(request.user)
			return HttpResponseRedirect(issue.get_absolute_url())
	else:
		form = EditIssueForm(instance=issue)
	data = { 'form': form, 'object': issue, 'action': 'update' }
	data.update(extra_context)
	return render_to_response(template, data, context_instance=RequestContext(request))

@login_required
def add_note(request, issue_id, extra_context={}, template='tracker/issue_add_note.html'):
	issue = get_object_or_404(Issue, id=issue_id)
	if request.method == 'POST':
		note = request.POST.get('note')
		if note is not None:
			issue.add_note(note, request.user)
			return HttpResponseRedirect(issue.get_absolute_url())
	else:
		form = AddNoteToIssueForm()
	data = { 'form': form, 'object': issue }
	data.update(extra_context)
	return render_to_response(template, data, context_instance=RequestContext(request))
