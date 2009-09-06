from django import template

register = template.Library()

def printuser(value):
	if not value:
		return u''
	return value.get_full_name() or value.username

register.filter(printuser)
