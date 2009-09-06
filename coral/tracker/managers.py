from django.db import models
from django.db.models import get_model

class IssuePriorityManager(models.Manager):
	def swap(self, item1, item2):
		p1 = item1.position
		p2 = item2.position
		
		item2.position = None
		item2.save()
		
		item1.position = p2
		item1.save()
		item2.position = p1
		item2.save()

class IssueManager(models.Manager):
	def open(self):
		return self.exclude(status='closed')
	
	def closed(self):
		return self.filter(status='closed')
