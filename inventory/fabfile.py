#from __future__ import with_statement

import os
from os.path import expanduser
import posixpath
from datetime import datetime
import pprint
#import re

from fabric.api import cd,lcd,local,require,run,settings,sudo,execute,task,put
from fabric.state import env
from fabric.colors import cyan,red
from fabric.context_managers import shell_env
from fabric.contrib.files import exists as fab_exists,upload_template
from fabric.utils import fastprint,abort

STAGES = {
    'dev': {
        'hosts' : ['localhost'],
        'root'  : os.path.join(expanduser("~"), 'webapps'),
        'sudo'  : '',
        },
    'prod': {
        'chown_user'  : 'dev',
        'chown_group' : 'webapps',
        'hosts'       : ['localhost'],
        'root'        : '/opt/webapps',
        'sudo'        : 'sudo',
        },
    'test': {
        'hosts': ['localhost'],
        'root': os.path.join(expanduser("~"), 'webapps'),
        },
}

REQUIRED_PKGS = ('supervisor',
                 'python-pip',
                 'python-virtualenv',
                 'python-dev',
                 'libpq-dev',
                )

APPCONF_FILES = (("inv-supervisord.jinja", "inv-supervisord.conf"),
                 ("gunicorn_start.jinja", "gunicorn_start.sh"),
                 ("inv-nginx.jinja", "inv-nginx.conf"),
                 ("default_settings.jinja", "default_settings.py"),
                )

def _set_stage(stage_name='test'):
    env.environment = stage_name
    for option, value in STAGES[env.environment].items():
        setattr(env, option, value)

    env.appname = os.path.basename(os.path.abspath(os.path.dirname(__file__)))
    env.deploydir = os.path.abspath(os.path.join(env.root, env.appname))
    env.virtualenv_dir = os.path.join(env.deploydir,'virtualenv')

    groupname = getattr(env, "chown_group", None)
    if groupname is None:
        setattr(env, "chown_group", env.user)

    username = getattr(env, "chown_user", None)
    if username is None:
        setattr(env, "chown_user", env.user)

@task
def dev():
    """ select development environment for deployment. """
    _set_stage('dev')

@task
def prod():
    """ select production environment for deployment. """
    _set_stage('prod')

def _release_name():
    """ use hg to determine current rev id and tag the deployment. """
    fastprint("Using 'hg id' to set release version.\n")

    current_rev = local('hg id', capture=True)
    return current_rev

def _pkg_check():
    """ Use dpkg to determine if the system has the required system packages. """
    fastprint("Checking for required system packages.")
    status = False

    for package in REQUIRED_PKGS:
        check = _package_installed(package)
        if not check:
            status = True

    return status

def _package_installed(pkg_name):
    """ref: http:superuser.com/questions/427318/#comment490784_427339"""
    cmd_f = 'dpkg-query -l "%s" | grep -q ^.i'
    cmd = cmd_f % (pkg_name)
    with settings(warn_only=True):
        result = run(cmd)
    return result.succeeded

def _prep_deploy_dest():
    """ Setup the base app directory structure."""
    if env.sudo:
        fastprint("Preparing Deployment Directory base (using sudo).\n")
        sudo('mkdir -p %s' % env.root)
        sudo('mkdir -p %s' % env.deploydir)
        sudo('mkdir -p %s' % env.virtualenv_dir)
        sudo('mkdir -p %s' % os.path.join(env.deploydir, 'appconf'))
        sudo('mkdir -p %s' % os.path.join(env.deploydir, 'bootstrap'))
        put('bootstrap/*', os.path.join(env.deploydir, 'bootstrap'), use_sudo=True)
        sudo('mkdir -p %s' % os.path.join(env.deploydir, 'logs'))
        sudo('mkdir -p %s' % os.path.join(env.deploydir, 'run'))
        sudo('mkdir -p %s' % os.path.join(env.deploydir, 'data'))
        sudo('chown -R %s:%s %s' % (env.chown_user, env.chown_group, env.deploydir))

    else:
        fastprint("Preparing Deployment Directory base.\n")
        run('mkdir -p %s' % env.root)
        run('mkdir -p %s' % env.deploydir)
        run('mkdir -p %s' % env.virtualenv_dir)
        run('mkdir -p %s' % os.path.join(env.deploydir, 'appconf'))
        run('mkdir -p %s' % os.path.join(env.deploydir, 'bootstrap'))
        put('bootstrap/*', os.path.join(env.deploydir, 'bootstrap'))
        run('mkdir -p %s' % os.path.join(env.deploydir, 'logs'))
        run('mkdir -p %s' % os.path.join(env.deploydir, 'run'))
        run('mkdir -p %s' % os.path.join(env.deploydir, 'data'))


def _setup_local_virtualenv(virtualenv_dir):
    # Create a new virtualenv
    activate = posixpath.join(virtualenv_dir, 'bin', 'activate')
    requirements = posixpath.join('bootstrap', 'requirements.txt')

    with cd(env.deploydir):
        if env.sudo:
            sudo('virtualenv --clear --no-site-packages virtualenv') 
            sudo('. %s && pip install pip --quiet --upgrade && pip install --quiet --requirement %s' % (activate, requirements))
            sudo('chown -R %s:%s %s' % (env.chown_user, env.chown_group, env.deploydir))
        else:
            local('virtualenv --clear --no-site-packages virtualenv')
            local('. %s && pip install pip --quiet --upgrade && pip install --quiet --requirement %s' % (activate, requirements))

def _copy_release(releasepath):
    # Copy the release code files over.

    dest = os.path.join(env.deploydir, releasepath)

    fastprint("Copying codefiles over to Deploy Directory...\n")
    if env.sudo:
        sudo('mkdir -p %s' % dest)
        put('code/*', dest, use_sudo=True)
        sudo('chown -R %s:%s %s' % (env.chown_user, env.chown_group, dest))
    else:
        run('mkdir -p %s' % dest)
        put('code/*', dest)

def _deploy_appconf():
    """
    jinja renders appconf files.
    """
    appconf = {'app_shortname'  : env.app_shortname,
               'app_name'       : env.appname,
               'deploy_dir'     : env.deploydir,
               'virtualenv_dir' : env.virtualenv_dir,
               'app_user'       : env.chown_user,
               'app_group'      : env.chown_group,
              }

    if env.sudo:
        usesudo = True
    else:
        usesudo = False
    
    for template,conffile in APPCONF_FILES:
        print red("%s :: %s" % (template, conffile))
        upload_template(template, os.path.join(env.deploydir, 'appconf', conffile), context=appconf, use_jinja=True, template_dir='appconf', use_sudo=usesudo)

def _symlink_release(releasepath, appname):
    # Force move the symlink to the current release.

    source = os.path.join(env.deploydir, releasepath)
    dest = os.path.join(env.deploydir, appname)

    fastprint("Symlinking %s to %s...\n" % (releasepath, appname))
    if env.sudo:
        sudo('ln -fns %s %s' % (source, dest))
    else:
        run('ln -fns %s %s' % (source, dest))

@task
def bootstrap():
    """
    
    """
    pkg_list = " ".join(map(str, REQUIRED_PKGS))
    fastprint("Running apt-get update...")
    sudo('apt-get --quiet update')
    fastprint("Installing required packages...")
    sudo('apt-get --quiet -y install %s' % pkg_list)
    fastprint("Package installation completed.")

@task
def deploy():
    """
    Deploys the latest rev for use
    """

    env.currentrev = _release_name()
    env.app_shortname = env.appname[:3].upper()
    env.releasepath = env.app_shortname + "-" + env.currentrev[:12]
    print cyan("Release: %s" % env.releasepath)

    print red("Deployment user: %s" % env.user)

    pkg_health = _pkg_check()

    if pkg_health:
        abort("One or more required system packages are unavailable.\n\nTry 'fab bootstrap'ing this system or installing the required package(s) by hand.")

    _prep_deploy_dest()
    with lcd(env.deploydir):
        _setup_local_virtualenv(env.virtualenv_dir)

    _copy_release(env.releasepath)
    _deploy_appconf()

    _symlink_release(env.releasepath, env.app_shortname)

@task
def dump():
    """
    dumps diag data
    """

    #pprint.pprint(env)
    pkg_health = _pkg_check()

    if pkg_health:
        abort("One or more required system packages are unavailable.\n\nTry 'fab bootstrap'ing this system or installing the required package(s) by hand.")

@task
def test():
    """
    Test functions from here.
    """
    _deploy_appconf()

@task
def help():
    message = '''
    Remote updating application with fabric.

    Usage example:

    Deploy to development server:
    fab dev deploy

    Deploy to production server:
    fab prod deploy
    '''
    fastprint(message)
