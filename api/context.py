import threading

context = threading.local()

def set_tenant(tenant):
    global context
    context.tenant = tenant

def get_tenant():
    global context
    return context.tenant

def del_tenant():
    global context
    del context.tenant
