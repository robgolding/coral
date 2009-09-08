from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list

from forms import NewIssueForm, EditIssueForm, AddNoteToIssueForm
from models import Issue, IssuePriority
from tagging.models import TaggedItem
import settings

def index(request, extra_context={}, template_name='index.html'):
	data = { }
	object_list = request.user.assigned.all()
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

def api(request):
	try:	
		issue_id = request.GET.get('issue_id')
		issue = Issue.objects.get(pk=issue_id)
	except Issue.DoesNotExist:
		error = True
	else:
		error = False
		if issue.is_starred_for(request.user):
			issue.unstar_for(request.user)
			starred = 'false'
		else:
			issue.star_for(request.user)
			starred = 'true'
	if not error:
		data = """
			{
				"result": true,
				"starred": %s
			}""" % starred
	else:
		data = """
			{
				"result": false
			}"""

	return HttpResponse(data, mimetype="application/javascript")
