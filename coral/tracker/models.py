## Skeleton models file for Bug Tracker
from django.db import models
from django.db.models import get_model
from django.db.models import signals
from django.db.models.signals import pre_save
from django.contrib.auth.models import User

from tagging.fields import TagField

from managers import IssueManager, IssuePriorityManager
import settings
from utils import get_changes_between_models

import datetime

ISSUE_PRIORITY_LEVELS = (
				(1, 1),
				(2, 2),
				(3, 3),
				(4, 4),
				(5, 5)
)

ISSUE_STATUS_CHOICES = (
				('active', 'Active'),
				('resolved', 'Resolved'),
				('closed', 'Closed'),
)

ISSUE_CHANGE_FIELDS = (
				('assigned_to', 'Assigned to'),
				('status', 'Status'),
				('priority', 'Priority'),
)

class IssueChange(models.Model):
	action = models.ForeignKey('IssueAction', related_name='changes')
	change_field = models.CharField(max_length=255, choices=ISSUE_CHANGE_FIELDS)
	old_value = models.CharField(max_length=255)
	new_value = models.CharField(max_length=255)
	
	def __unicode__(self):
		return '[IssueChange] %s changed from %s to %s' % (self.get_change_field_display(), self.old_value, self.new_value)
	
	def get_old_or_new_value(self, old_or_new_value):
		if old_or_new_value == 'old_value' or old_or_new_value == 'new_value':
			model = self.action.issue.__class__
			if isinstance(model._meta.get_field(self.change_field), models.ForeignKey):
				return self.action.issue.__getattribute__(self.change_field).__class__._default_manager.get(pk=self.__getattribute__(old_or_new_value))
			elif hasattr(model, 'get_%s_display' % self.change_field):
				issue = model()
				value = self.__getattribute__(old_or_new_value)
				if isinstance(issue._meta.get_field(self.change_field), models.IntegerField):
					value = int(value)
				issue.__setattr__(self.change_field, value)
				return issue._get_FIELD_display(issue._meta.get_field(self.change_field))
			else:
				return self.__getattribute__(old_or_new_value)
		else:
			raise ValueError, 'get_old_or_new_value must be supplied either "old_value" or "new_value"'
	
	def get_old_value(self):
		return self.get_old_or_new_value('old_value')
	
	def get_new_value(self):
		return self.get_old_or_new_value('new_value')

class IssueAction(models.Model):
	issue = models.ForeignKey('Issue', related_name='actions')
	notes = models.TextField()
	performed_at = models.DateTimeField(auto_now=True)
	performed_by = models.ForeignKey(User)
	
	@property
	def has_content(self):
		return self.notes or self.changes.all()
	
	def __unicode__(self):
		return '[IssueAction] on issue #%s at %s' % (self.issue.id, self.performed_at)
	
	class Meta:
		ordering = ['performed_at']

class Star(models.Model):
	issue = models.ForeignKey('Issue', related_name='stars')
	user = models.ForeignKey(User, related_name='stars')
	
	class Meta:
		unique_together = ('issue', 'user',)
	
	def __unicode__(self):
		return '%s [%s]' % (self.issue, self.user)

class IssuePriority(models.Model):
	name = models.CharField(max_length=255)
	level = models.IntegerField(choices=ISSUE_PRIORITY_LEVELS)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		verbose_name_plural = 'Issue priorities'
		ordering = ['level', 'name']
		

class Issue(models.Model):
	raised_by = models.ForeignKey(User, related_name='raised')
	assigned_to = models.ForeignKey(User, related_name='assigned')
	originally_assigned_to = models.ForeignKey(User, editable=False)
	priority = models.ForeignKey(IssuePriority)
	title = models.CharField(max_length=255)
	description = models.TextField()
	status = models.CharField(max_length=20, choices=ISSUE_STATUS_CHOICES)
	created_at = models.DateTimeField(auto_now_add=True)
	last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
	
	tags = TagField()
	
	objects = IssueManager()
	
	def __unicode__(self):
		return '%s - %s' % (self.id, self.title)
	
	def save(self, force_insert=False, force_update=False):
		if not self.id:
			self.originally_assigned_to = self.assigned_to
		super(self.__class__, self).save(force_insert, force_update)
		
	
	def _get_changes(self, new_issue):
		changes = {}
		for field, _ in ISSUE_CHANGE_FIELDS:
			old_value = self.__getattribute__(field)
			new_value = new_issue.__getattribute__(field)
			if old_value != new_value:
				if isinstance(Issue._meta.get_field(field), models.ForeignKey):
					old_value = old_value._get_pk_val()
					new_value = new_value._get_pk_val()
				changes[field] = (old_value, new_value)
		return changes
	
	def register_action(self, new_issue, notes, user):
		changes = self._get_changes(new_issue)
		if notes or changes:
			if not notes: notes = ''
			action = IssueAction(issue=self, notes=notes, performed_by=user)
			action.save()
			for field, values in changes.items():
					IssueChange(action=action, change_field=field, old_value=values[0], new_value=values[1]).save()
	
	def add_note(self, note, user):
		IssueAction(issue=self, notes=note, performed_by=user).save()
	
	def is_starred_for(self, user):
		return user in self.starred_for
	
	def star_for(self, user):
		return Star.objects.get_or_create(issue=self, user=user)
	
	def unstar_for(self, user):
		try:
			star = Star.objects.get(issue=self, user=user)
		except Star.DoesNotExist:
			return
		star.delete()
	
	@models.permalink
	def get_absolute_url(self):
		return ('tracker_issue_detail', (), {'object_id': self.id})
	
	@property
	def is_editable(self):
		delta = datetime.timedelta(seconds=settings.ISSUE_DESCRIPTION_EDITABLE_SECONDS)
		return self.created_at > datetime.datetime.now() - delta
	
	@property
	def editable_timeleft(self):
		delta = datetime.timedelta(seconds=settings.ISSUE_DESCRIPTION_EDITABLE_SECONDS)
		if not self.is_editable:
			return None
		return int(round(((delta - (datetime.datetime.now() - self.created_at)).seconds/60)))
	
	@property
	def starred_for(self):
		return list(set([star.user for star in self.stars.all()]))
	
	@property
	def has_history(self):
		if not self.actions.count():
			return False
		for action in self.actions.all():
			if action.has_content:
				return True
		return False
	
	def get_tags(self):
		from tagging.models import Tag
		return Tag.objects.get_for_object(self)
	
	class Meta:
		verbose_name_plural = 'Issues'
		ordering = ['-last_updated', '-priority__level']
