"""
Starter fabfile for deploying a Django project.

Derived from https://bitbucket.org/spookylukey/django-fabfile-starter/raw/f4c87b0b2676/fabfile.py

Change all the things marked CHANGEME. Other things can be left at their
defaults if you are happy with the default layout.
"""

import posixpath

from fabric.api import run, local, abort, env, put, settings, cd, task
from fabric.contrib import django
from fabric.decorators import runs_once
from fabric.contrib.files import exists
from fabric.context_managers import cd, lcd, settings, hide

import sys
sys.path.append('.')
django.settings_module('hello.hello.settings')


@task
def pull(ref='origin/master'):
    """
	Update the code from the src repo

	defaults to production branch
	on admin server
	local('git reset --hard %s' % ref, capture=False)
    """
    from django.conf import settings
    print settings.TIME_ZONE
    print "Moo"
    if ref:
        local('git reset --hard %s' % ref, capture=True)
        print ref
    local('ls')
    pass


def virtualenv(venv_dir):
    """
    Context manager that establishes a virtualenv to use.
    """
    return settings(venv=venv_dir)


def run_venv(command, **kwargs):
    """
    Runs a command in a virtualenv (which has been specified using
    the virtualenv context manager
    """
    run("source %s/bin/activate" % env.venv + " && " + command, **kwargs)


def install_dependencies():
    ensure_virtualenv()
    with virtualenv(venv_dir):
        with cd(src_dir):
            run_venv("pip install -r requirements.txt")


def ensure_virtualenv():
    if exists(venv_dir):
        return

    with cd(DJANGO_APP_ROOT):
        run("virtualenv --no-site-packages --python=%s %s" %
            (PYTHON_BIN, VENV_SUBDIR))
        run("echo %s > %s/lib/%s/site-packages/projectsource.pth" %
            (src_dir, VENV_SUBDIR, PYTHON_BIN))


def ensure_src_dir():
    if not exists(src_dir):
        run("mkdir -p %s" % src_dir)
    with cd(src_dir):
        if not exists(posixpath.join(src_dir, '.hg')):
            run("hg init")


def push_sources():
    """
    Push source code to server
    """
    ensure_src_dir()
    local("hg push -f ssh://%(user)s@%(host)s/%(path)s" %
          dict(host=env.host,
               user=env.user,
               path=src_dir,
               ))
    with cd(src_dir):
        run("hg update")


@task
def webserver_stop():
    """
    Stop the webserver that is running the Django instance
    """
    run(DJANGO_SERVER_STOP)


@task
def webserver_start():
    """
    Startsp the webserver that is running the Django instance
    """
    run(DJANGO_SERVER_START)


@task
def webserver_restart():
    """
    Restarts the webserver that is running the Django instance
    """
    if DJANGO_SERVER_RESTART:
        run(DJANGO_SERVER_RESTART)
    else:
        with settings(warn_only=True):
            webserver_stop()
        webserver_start()


def build_static():
    assert STATIC_ROOT.strip() != '' and STATIC_ROOT.strip() != '/'
    # Before Django 1.4 we don't have the --clear option to collectstatic
    run("rm -rf %s/*" % STATIC_ROOT)

    with virtualenv(venv_dir):
        with cd(src_dir):
            run_venv("./manage.py collectstatic -v 0 --noinput")

    run("chmod -R ugo+r %s" % STATIC_ROOT)


@task
def first_deployment_mode():
    """
    Use before first deployment to switch on fake south migrations.
    """
    env.initial_deploy = True


def update_database():
    with virtualenv(venv_dir):
        with cd(src_dir):
            if getattr(env, 'initial_deploy', False):
                run_venv("./manage.py syncdb --all")
                run_venv("./manage.py migrate --fake --noinput")
            else:
                run_venv("./manage.py syncdb --noinput")
                run_venv("./manage.py migrate --noinput")


@task
def deploy():
    """
    Deploy project.
    """
    with settings(warn_only=True):
        webserver_stop()
    push_sources()
    install_dependencies()
    update_database()
    build_static()

    webserver_start()