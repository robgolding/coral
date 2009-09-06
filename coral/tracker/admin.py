from models import Issue, IssueAction, IssueChange, IssuePriority
from django.contrib import admin

admin.site.register(Issue)
admin.site.register(IssueAction)
admin.site.register(IssueChange)
admin.site.register(IssuePriority)

