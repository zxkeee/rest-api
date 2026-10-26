from django.urls import path

from . import views

urlpatterns = [
    path('languages/', views.LanguageList.as_view()),
    path('languages/<int:pk>/', views.LanguageDetail.as_view()),
    path('organizations/', views.OrganizationList.as_view()),
    path('organizations/<int:pk>/', views.OrganizationDetail.as_view()),
    path('organizations/<int:pk>/projects/', views.OrganizationProjects.as_view()),
    path('maintainers/', views.MaintainerList.as_view()),
    path('maintainers/<int:pk>/', views.MaintainerDetail.as_view()),
    path('maintainers/<int:pk>/projects/', views.MaintainerProjects.as_view()),
    path('projects/', views.ProjectList.as_view()),
    path('projects/<int:pk>/', views.ProjectDetail.as_view()),
    path('issues/', views.IssueList.as_view()),
    path('issues/<int:pk>/', views.IssueDetail.as_view()),
]
