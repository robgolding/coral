from django.conf.urls.defaults import *
from django.contrib import admin

import views

urlpatterns = patterns('',
	
	url(r'^tags/$', views.filter_tags, name="filter_tags"),
	
)
