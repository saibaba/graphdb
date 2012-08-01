import threading
import webapp2
import logging
from webapp2_extras import sessions

context = threading.local()

def set_tenant(tenant, scope="request"):
    global context

    if scope == "request":
        context.tenant = tenant
        webapp2.get_request().environ['IN_SESSION'] = False
    else:
        logging.info("**** Storing tenant in session...")
        webapp2.get_request().environ['IN_SESSION'] = True
        sessions.get_store().get_session()['TENANT'] = tenant

def get_tenant():

    global context

    tenant = None

    in_session = webapp2.get_request().environ.get('IN_SESSION')

    if not in_session:
        if hasattr(context, 'tenant'):
            tenant =  context.tenant
        else:
            webapp2.abort(403, "No current tenant found")
    else:
        s = sessions.get_store().get_session()
        if 'TENANT' in  s:
            tenant = s['TENANT']
        else:
            webapp2.abort(403, "No current tenant found")

    return tenant

def del_tenant(scope="request"):
    global context

    in_session = webapp2.get_request().environ.get('IN_SESSION')

    if not in_session:
        del context.tenant
    else:
        s = sessions.get_store().get_session()
        if 'TENANT' in  s:
            del s['TENANT']

