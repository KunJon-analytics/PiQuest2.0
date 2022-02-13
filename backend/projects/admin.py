from django.contrib import admin

# Register your models here.
from .models import Project, ArticleLink


admin.site.register(Project)
admin.site.register(ArticleLink)