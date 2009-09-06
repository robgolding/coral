from django.shortcuts import render_to_response
from django.template import RequestContext

from django.db.models import get_model

def filter_tags(request, extra_context={}, template='filter/templates/generic.html'):
	model = get_model('tagging', 'Tag')
	q = request.GET.get('q')
	if not q:
		tags = []
	else:
		limit = request.GET.get('limit')
		if not limit:
			limit = 6
		tags = model.objects.filter(name__startswith=q)[:limit]
	data = {'object_list': tags}
	data.update(extra_context)
	return render_to_response(template, data, context_instance=RequestContext(request), mimetype="text/plain")
