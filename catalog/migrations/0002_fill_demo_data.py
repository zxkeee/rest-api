from django.db import migrations


def fill_demo_data(apps, schema_editor):
    Language = apps.get_model('catalog', 'Language')
    Organization = apps.get_model('catalog', 'Organization')
    Maintainer = apps.get_model('catalog', 'Maintainer')
    Project = apps.get_model('catalog', 'Project')
    Issue = apps.get_model('catalog', 'Issue')

    python = Language.objects.create(name='Python')
    javascript = Language.objects.create(name='JavaScript')
    typescript = Language.objects.create(name='TypeScript')
    rust = Language.objects.create(name='Rust')
    Language.objects.create(name='Go')

    django_org = Organization.objects.create(name='Django Software Foundation', github_url='https://github.com/django')
    psf = Organization.objects.create(name='Python Software Foundation', github_url='https://github.com/python')
    microsoft = Organization.objects.create(name='Microsoft', github_url='https://github.com/microsoft')
    Organization.objects.create(name='Mozilla', github_url='https://github.com/mozilla')

    felix = Maintainer.objects.create(full_name='Felix Kling', github_username='fkling')
    sarah = Maintainer.objects.create(full_name='Sarah Boyce', github_username='sarahboyce')
    hugo = Maintainer.objects.create(full_name='Hugo van Kemenade', github_username='hugovk')
    Maintainer.objects.create(full_name='Ivan Petrenko', github_username='ivan-petrenko')

    django_project = Project.objects.create(
        name='Django',
        description='The web framework for perfectionists with deadlines.',
        repo_url='https://github.com/django/django',
        stars=81000,
        difficulty='intermediate',
        maintainer=sarah,
        organization=django_org,
    )
    django_project.languages.add(python, javascript)

    cpython = Project.objects.create(
        name='CPython',
        description='The Python programming language.',
        repo_url='https://github.com/python/cpython',
        stars=63000,
        difficulty='advanced',
        maintainer=hugo,
        organization=psf,
    )
    cpython.languages.add(python)

    peps = Project.objects.create(
        name='PEPs',
        description='Python Enhancement Proposals.',
        repo_url='https://github.com/python/peps',
        stars=4300,
        difficulty='beginner',
        maintainer=hugo,
        organization=psf,
    )
    peps.languages.add(python)

    vscode = Project.objects.create(
        name='Visual Studio Code',
        description='Code editor by Microsoft.',
        repo_url='https://github.com/microsoft/vscode',
        stars=165000,
        difficulty='intermediate',
        maintainer=felix,
        organization=microsoft,
    )
    vscode.languages.add(typescript, javascript)

    windows_rs = Project.objects.create(
        name='Rust for Windows',
        description='Rust bindings for Windows APIs.',
        repo_url='https://github.com/microsoft/windows-rs',
        stars=10500,
        difficulty='advanced',
        maintainer=felix,
        organization=microsoft,
    )
    windows_rs.languages.add(rust)

    Issue.objects.create(project=django_project, title='Fix typo in tutorial part 2', difficulty='beginner', status='open')
    Issue.objects.create(project=django_project, title='Add missing translation strings', difficulty='beginner', status='in_progress')
    Issue.objects.create(project=cpython, title='Improve error message for unclosed bracket', difficulty='intermediate', status='open')
    Issue.objects.create(project=peps, title='Fix broken link in PEP 8', difficulty='beginner', status='closed')
    Issue.objects.create(project=vscode, title='Update README screenshots', difficulty='beginner', status='closed')
    Issue.objects.create(project=windows_rs, title='Add example for clipboard API', difficulty='intermediate', status='open')


def clear_demo_data(apps, schema_editor):
    apps.get_model('catalog', 'Issue').objects.all().delete()
    apps.get_model('catalog', 'Project').objects.all().delete()
    apps.get_model('catalog', 'Maintainer').objects.all().delete()
    apps.get_model('catalog', 'Organization').objects.all().delete()
    apps.get_model('catalog', 'Language').objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fill_demo_data, clear_demo_data),
    ]
