from django.contrib import admin

from .models import Issue, Language, Maintainer, Organization, Project


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'difficulty', 'stars', 'organization', 'maintainer')


class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'difficulty', 'status')


admin.site.register(Language)
admin.site.register(Organization)
admin.site.register(Maintainer)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Issue, IssueAdmin)
