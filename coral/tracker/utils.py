from django.db.models import fields

def get_changes_between_models(model1, model2, fields=[]):
	changes = {}
	for field in fields:
		if model1.__getattribute__(field) != model2.__getattribute__(field):
			changes[field] = (model1._meta.get_field(field).value_from_object(model1), 
								model2._meta.get_field(field).value_from_object(model2),)
	return changes

def get_stats():
	from models import Issue
	from django.contrib.auth.models import User
	stats = {}
	stats['total_issues'] = Issue.objects.all().count()
	stats['open_issues'] = Issue.objects.open().count()
	stats['closed_issues'] = Issue.objects.closed().count()
	stats['total_users'] = User.objects.all().count()
	return stats
