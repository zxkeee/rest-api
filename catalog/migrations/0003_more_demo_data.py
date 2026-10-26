from django.db import migrations

LANGUAGES = ['Java', 'C++', 'C#', 'Ruby', 'PHP', 'Dart']

ORGANIZATIONS = [
    ('Meta', 'https://github.com/facebook'),
    ('Google', 'https://github.com/google'),
    ('The Go Authors', 'https://github.com/golang'),
    ('Rust Foundation', 'https://github.com/rust-lang'),
    ('Vercel', 'https://github.com/vercel'),
    ('Ruby on Rails', 'https://github.com/rails'),
    ('Flutter', 'https://github.com/flutter'),
    ('Laravel', 'https://github.com/laravel'),
    ('freeCodeCamp', 'https://github.com/freeCodeCamp'),
    ('Home Assistant', 'https://github.com/home-assistant'),
]

MAINTAINERS = [
    ('Olena Koval', 'olena-koval'),
    ('Andrii Melnyk', 'amelnyk-dev'),
    ('Mariia Shevchuk', 'mshevchuk'),
    ('Taras Bondar', 'tbondar'),
]

PROJECTS = [
    ('React', 'The library for web and native user interfaces.', 'https://github.com/facebook/react', 230000, 'intermediate', ['JavaScript'], 'olena-koval', 'Meta'),
    ('Guava', 'Google core libraries for Java.', 'https://github.com/google/guava', 50000, 'intermediate', ['Java'], 'amelnyk-dev', 'Google'),
    ('GoogleTest', 'Google testing and mocking framework.', 'https://github.com/google/googletest', 36000, 'advanced', ['C++'], 'amelnyk-dev', 'Google'),
    ('Go', 'The Go programming language.', 'https://github.com/golang/go', 124000, 'advanced', ['Go'], 'tbondar', 'The Go Authors'),
    ('Rust', 'Empowering everyone to build reliable and efficient software.', 'https://github.com/rust-lang/rust', 100000, 'advanced', ['Rust'], 'tbondar', 'Rust Foundation'),
    ('Rustlings', 'Small exercises to get you used to reading and writing Rust code.', 'https://github.com/rust-lang/rustlings', 55000, 'beginner', ['Rust'], 'tbondar', 'Rust Foundation'),
    ('Next.js', 'The React framework.', 'https://github.com/vercel/next.js', 128000, 'intermediate', ['JavaScript', 'TypeScript'], 'olena-koval', 'Vercel'),
    ('Ruby on Rails', 'Web application framework with everything needed to build database-backed apps.', 'https://github.com/rails/rails', 56000, 'intermediate', ['Ruby'], 'mshevchuk', 'Ruby on Rails'),
    ('Flutter', 'Build apps for any screen from one codebase.', 'https://github.com/flutter/flutter', 167000, 'advanced', ['Dart'], 'mshevchuk', 'Flutter'),
    ('Laravel', 'Skeleton application for the Laravel framework.', 'https://github.com/laravel/laravel', 79000, 'beginner', ['PHP'], 'mshevchuk', 'Laravel'),
    ('freeCodeCamp', 'Open-source curriculum for learning to code.', 'https://github.com/freeCodeCamp/freeCodeCamp', 400000, 'beginner', ['TypeScript', 'JavaScript'], 'olena-koval', 'freeCodeCamp'),
    ('Home Assistant', 'Open source home automation.', 'https://github.com/home-assistant/core', 75000, 'intermediate', ['Python'], 'amelnyk-dev', 'Home Assistant'),
    ('PDF.js', 'PDF reader in JavaScript.', 'https://github.com/mozilla/pdf.js', 49000, 'intermediate', ['JavaScript'], 'ivan-petrenko', 'Mozilla'),
    ('TypeScript', 'JavaScript with syntax for types.', 'https://github.com/microsoft/TypeScript', 101000, 'advanced', ['TypeScript'], 'fkling', 'Microsoft'),
    ('PowerToys', 'Utilities for power users on Windows.', 'https://github.com/microsoft/PowerToys', 112000, 'intermediate', ['C#'], 'fkling', 'Microsoft'),
    ('Requests', 'A simple HTTP library for Python.', 'https://github.com/psf/requests', 52000, 'beginner', ['Python'], 'hugovk', 'Python Software Foundation'),
    ('Black', 'The uncompromising Python code formatter.', 'https://github.com/psf/black', 39000, 'beginner', ['Python'], 'hugovk', 'Python Software Foundation'),
]

ISSUES = [
    ('React', 'Clarify useEffect cleanup example in docs', 'beginner', 'open'),
    ('Guava', 'Add Javadoc example for ImmutableList.builder', 'beginner', 'open'),
    ('Go', 'Improve error text for unused imports', 'intermediate', 'in_progress'),
    ('Rustlings', 'Add hint for the iterators3 exercise', 'beginner', 'open'),
    ('Rustlings', 'Fix typo in the README of the structs section', 'beginner', 'closed'),
    ('Next.js', 'Update example with app router', 'intermediate', 'open'),
    ('Ruby on Rails', 'Document default value of config.time_zone', 'beginner', 'open'),
    ('Laravel', 'Translate validation messages to Ukrainian', 'beginner', 'open'),
    ('freeCodeCamp', 'Fix broken link in the JavaScript course', 'beginner', 'open'),
    ('freeCodeCamp', 'Add alt text to images in lesson 12', 'beginner', 'in_progress'),
    ('Home Assistant', 'Add unit test for the weather sensor', 'intermediate', 'open'),
    ('PDF.js', 'Keyboard shortcut list is missing zoom keys', 'beginner', 'closed'),
    ('Requests', 'Add example for timeout parameter', 'beginner', 'open'),
    ('Black', 'Add test case for long string concatenation', 'intermediate', 'open'),
]


def fill_more_demo_data(apps, schema_editor):
    Language = apps.get_model('catalog', 'Language')
    Organization = apps.get_model('catalog', 'Organization')
    Maintainer = apps.get_model('catalog', 'Maintainer')
    Project = apps.get_model('catalog', 'Project')
    Issue = apps.get_model('catalog', 'Issue')

    for name in LANGUAGES:
        Language.objects.create(name=name)
    for name, github_url in ORGANIZATIONS:
        Organization.objects.create(name=name, github_url=github_url)
    for full_name, github_username in MAINTAINERS:
        Maintainer.objects.create(full_name=full_name, github_username=github_username)

    for name, description, repo_url, stars, difficulty, language_names, maintainer, organization in PROJECTS:
        project = Project.objects.create(
            name=name,
            description=description,
            repo_url=repo_url,
            stars=stars,
            difficulty=difficulty,
            maintainer=Maintainer.objects.get(github_username=maintainer),
            organization=Organization.objects.get(name=organization),
        )
        project.languages.add(*Language.objects.filter(name__in=language_names))

    for project_name, title, difficulty, status in ISSUES:
        Issue.objects.create(
            project=Project.objects.get(name=project_name),
            title=title,
            difficulty=difficulty,
            status=status,
        )


def clear_more_demo_data(apps, schema_editor):
    Project = apps.get_model('catalog', 'Project')
    Project.objects.filter(repo_url__in=[project[2] for project in PROJECTS]).delete()
    apps.get_model('catalog', 'Maintainer').objects.filter(github_username__in=[m[1] for m in MAINTAINERS]).delete()
    apps.get_model('catalog', 'Organization').objects.filter(name__in=[o[0] for o in ORGANIZATIONS]).delete()
    apps.get_model('catalog', 'Language').objects.filter(name__in=LANGUAGES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_fill_demo_data'),
    ]

    operations = [
        migrations.RunPython(fill_more_demo_data, clear_more_demo_data),
    ]
