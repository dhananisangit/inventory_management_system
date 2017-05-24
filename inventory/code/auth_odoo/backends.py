# Class for Authenticating against and odoo/openerp instance via xmlrpc

# Manufacturing Manager: 19
# Warehouse Manager: 23
# Shipping Manager: 94

from django.contrib.auth.models import User
import oerplib

#import pprint

class OdooBackendException(Exception):
    pass

class OdooBackend(object):

    def authenticate(self, username=None, password=None):
        if not hasattr(self, "odoo_settings"):
            self.odoo_settings = OdooSettings()
        odoo = oerplib.OERP(self.odoo_settings.HOSTNAME, protocol=self.odoo_settings.PROTOCOL, port=self.odoo_settings.BINDPORT)

        try:
            user = odoo.login(username, password, self.odoo_settings.DATABASE)
        except OdooBackendException:
            return None
        except oerplib.error.RPCError:
            return None
        if (user.id):
            user_data = odoo.execute('res.users', 'read', [user.id])
            for gid in self.odoo_settings.GROUPFILTER:
                if (gid not in user_data[0]['groups_id']):
                    #print "GID: " + str(gid) + " not matched."
                    return None

            try:
                user = User.objects.get(username=user_data[0]['login'])
            except User.DoesNotExist:
                user = User(username=user_data[0]['login'],
                            first_name=user_data[0]['name'].split()[0],
                            last_name=user_data[0]['name'].split()[-1],
                            email=user_data[0]['email'],
                            )
                user.set_unusable_password()
                user.save()
            
            return user
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
             
# Load settings from Django settings

class OdooSettings(object):
    defaults = {
        'HOSTNAME': {},
        'PROTOCOL': {},
        'BINDPORT': {},
        'DATABASE': {},
        'GROUPFILTER': [1]
    }

    def __init__(self, prefix='AUTH_ODOO_'):
        
        from django.conf import settings

        for name, default in self.defaults.items():
            value = getattr(settings, prefix + name, default)
            setattr(self, name, value)

