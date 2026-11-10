from rest_framework import serializers

from .models import Issue, Language, Maintainer, Organization, Project


def validate_github_url(value):
    if not value.startswith('https://github.com/'):
        raise serializers.ValidationError('Посилання має починатися з https://github.com/')
    return value


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name']


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'github_url']

    def validate_github_url(self, value):
        return validate_github_url(value)


class MaintainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintainer
        fields = ['id', 'full_name', 'github_username']


class ProjectSerializer(serializers.ModelSerializer):
    languages = serializers.PrimaryKeyRelatedField(many=True, queryset=Language.objects.all())

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'repo_url', 'stars', 'difficulty', 'languages', 'maintainer', 'organization']

    def validate_repo_url(self, value):
        return validate_github_url(value)

    def validate_stars(self, value):
        if value < 0:
            raise serializers.ValidationError('Кількість зірок не може бути відʼємною.')
        return value

    def validate_languages(self, value):
        if not value:
            raise serializers.ValidationError('Вкажіть хоча б одну мову програмування.')
        return value


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'project', 'title', 'difficulty', 'status']
