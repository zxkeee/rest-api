from django.db import models

DIFFICULTY_CHOICES = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
]

ISSUE_STATUS_CHOICES = [
    ('open', 'Open'),
    ('in_progress', 'In progress'),
    ('closed', 'Closed'),
]


class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Organization(models.Model):
    name = models.CharField(max_length=100)
    github_url = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Maintainer(models.Model):
    full_name = models.CharField(max_length=100)
    github_username = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f'{self.full_name} ({self.github_username})'


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    repo_url = models.CharField(max_length=200, unique=True)
    stars = models.IntegerField(default=0)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    languages = models.ManyToManyField(Language, related_name='projects')
    maintainer = models.ForeignKey(Maintainer, on_delete=models.PROTECT, related_name='projects')
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name='projects')

    def __str__(self):
        return self.name


class Issue(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    title = models.CharField(max_length=200)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    status = models.CharField(max_length=20, choices=ISSUE_STATUS_CHOICES, default='open')

    def __str__(self):
        return f'{self.project.name}: {self.title}'
