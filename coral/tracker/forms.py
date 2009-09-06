from django import forms

from django.contrib.auth.models import User
import models
from models import Issue

INITIAL_STATUS_VALUE = 'active'

class IssueForm(forms.ModelForm):
	
	class Meta:
		model = Issue
		exclude = ['raised_by']
		
class NewIssueForm(IssueForm):
	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)
		self.fields['status_dropdown'].widget.attrs['disabled'] = True
	
	status = forms.ChoiceField(widget=forms.HiddenInput, choices=models.ISSUE_STATUS_CHOICES, initial=INITIAL_STATUS_VALUE)
	status_dropdown = forms.ChoiceField(label="Status", choices=models.ISSUE_STATUS_CHOICES, initial=INITIAL_STATUS_VALUE, required=False)
	
	def save(self, user, commit=True):
		issue = super(self.__class__, self).save(commit=False)
		issue.raised_by = user
		if commit:
			issue.save()
		return issue
	
class EditIssueForm(IssueForm):
	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)
		if 'instance' in kwargs:
			instance = kwargs['instance']
			if instance.is_editable:
				self.fields['description'].label="Description"
				self.fields['title'].label="Title"
			else:
				self.fields.__delitem__('description')
				self.fields.__delitem__('title')
	
	notes = forms.CharField(widget=forms.Textarea, required=False)
	
	def save(self, user, commit=True):
		new_issue = super(self.__class__, self).save(commit=False)
		old_issue = Issue.objects.get(pk=new_issue.pk)
		old_issue.register_action(new_issue, self.cleaned_data['notes'], user)
		if commit:
			new_issue.save()
		return new_issue
	
	class Meta(IssueForm.Meta):
		exclude = ['raised_by']

class AddNoteToIssueForm(forms.Form):
	note = forms.CharField(widget=forms.Textarea, required=True)
