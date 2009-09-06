from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from profiles.views import profile_detail

from models import *

def user_detail(request, *args, **kwargs):
	user = get_object_or_404(User, username=kwargs['username'])
	try:
		user.get_profile()
	except:
		Profile(user=user).save()
	return profile_detail(request, *args, **kwargs)
