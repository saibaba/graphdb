# -*- coding: utf-8 -*-

"""


	A real simple app for using webapp2 with auth and session.

	It just covers the basics. Creating a user, login, logout and a decorator for protecting certain handlers.

	PRE-REQUIREMENTS:

	Set at secret_key in webapp2 config:
	webapp2_config = {}
	webapp2_config['webapp2_extras.sessions'] = {
		'secret_key': 'Im_an_alien',
	}

	You need to either set upp the following routes:

	app = webapp2.WSGIApplication([
		webapp2.Route(r'/login/', handler=LoginHandler, name='login'),
		webapp2.Route(r'/logout/', handler=LogoutHandler, name='logout'),
		webapp2.Route(r'/secure/', handler=SecureRequestHandler, name='secure'),
		webapp2.Route(r'/create/', handler=CreateUserHandler, name='create-user'),

	])

    OR:

    Change the urls in BaseHandler.auth_config to match LoginHandler/LogoutHandler
    And also change the url in the post method of the LoginHandler to redirect to to a page requiring a user session

    Notes/Reference:
        http://code.google.com/p/webapp-improved/issues/detail?id=20
        http://stackoverflow.com/questions/8550019/how-to-use-auth-with-webapp2-in-gae
        http://webapp-improved.googlecode.com/hg/tests/extras_auth_test.py?r=c84a093103d15166c8741c606e6663e9cc622aa2 - what i need i guess
        http://webapp-improved.googlecode.com/hg/tests/extras_security_test.py
        http://webapp-improved.googlecode.com/hg/tests/extras_appengine_auth_models_test.py


"""

import webapp2
from webapp2_extras import auth as wauth
from webapp2_extras import sessions
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError
import logging
from context import set_tenant

#@webapp2.cached_property
def auth():
    return wauth.get_auth()

#@webapp2.cached_property
def auth_config():
    """
        Dict to hold urls for login/logout
        webapp2.Route(r'/auth/login', handler=LoginHandler, name='login'),                                                                                                                                            
    """
    return {
        'login_url': r'/auth/login',    #webapp2.uri_for('login'),
        'logout_url': r'/auth/logout',   #webapp2.uri_for('logout'),
        'create_user_url': r'/auth/create-user',   #webapp2.uri_for('create-user'),
    }

def user_required(handler):
    """
         Decorator for checking if there's a user associated with the current session.
         Will also fail if there's no session present.
     """

    def check_api_login(self, *args, **kwargs):

        cred_passed  = False

        try:
            if 'X-Auth-User' in self.request.headers and 'X-Auth-Password' in self.request.headers:
                username = self.request.headers['X-Auth-User']
                password = self.request.headers['X-Auth-Password']
                auth().get_user_by_password(username, password)
                cred_passed  =  True
                set_tenant(username, "request")
        except (InvalidAuthIdError, InvalidPasswordError), e:
            logging.exception(e)

        return cred_passed
        
    def check_login(self, *args, **kwargs):


        if check_api_login(self, *args, **kwargs):
            return handler(self, *args, **kwargs)

        if not auth().get_user_by_session():
            # If handler has no login_url specified invoke a 403 error
            try:
                return self.redirect(auth_config()['login_url'], abort=False)
            except (AttributeError, KeyError), e:
                logging.exception("Error during redirect to login page!")
                logging.exception(e)
                self.abort(403)
        else:
            webapp2.get_request().environ['IN_SESSION'] = True
            return handler(self, *args, **kwargs)

    return check_login


class BaseHandler(webapp2.RequestHandler):
    """
         BaseHandler for all requests

         Holds the auth and session properties so they are reachable for all requests
     """

    def dispatch(self):
        """
              Save the sessions for preservation across requests
          """
        try:
            response = super(BaseHandler, self).dispatch()
            self.response.write(response)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session_store(self):
        return sessions.get_store(request=self.request)

class LoginHandler(BaseHandler):
    def get(self):
        """
              Returns a simple HTML form for login
          """
        return """
			<!DOCTYPE hml>
			<html>
				<head>
					<title>webapp2 auth example</title>
				</head>
				<body>
				<form action="%s" method="post">
					<fieldset>
						<legend>Login form</legend>
						<label>Username <input type="text" name="username" placeholder="Your username" /></label>
						<label>Password <input type="password" name="password" placeholder="Your password" /></label>
					</fieldset>
					<button>Login</button>
				</form>
                                <br />
                                Do not have an account? <a href="%s">Create</a> here, it is free!
			</html>
		""" % (self.request.url, auth_config()['create_user_url'] )

    def post(self):
        """
              username: Get the username from POST dict
              password: Get the password from POST dict
          """
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        # Try to login user with password
        # Raises InvalidAuthIdError if user is not found
        # Raises InvalidPasswordError if provided password doesn't match with specified user
        try:
            auth().get_user_by_password(username, password)
            set_tenant(username, "session")
            self.redirect('/graphdb/ref')
        except (InvalidAuthIdError, InvalidPasswordError), e:
            # Returns error message to self.response.write in the BaseHandler.dispatcher
            # Currently no message is attached to the exceptions
            return e


class CreateUserHandler(BaseHandler):
    def get(self):
        """
              Returns a simple HTML form for create a new user
          """
        return """
			<!DOCTYPE hml>
			<html>
				<head>
					<title>webapp2 auth example</title>
				</head>
				<body>
				<form action="%s" method="post">
					<fieldset>
						<legend>Create user form</legend>
						<label>Username <input type="text" name="username" placeholder="Your username" /></label>
						<label>Password <input type="password" name="password" placeholder="Your password" /></label>
					</fieldset>
					<button>Create user</button>
				</form>
			</html>
		""" % self.request.url

    def post(self):
        """
              username: Get the username from POST dict
              password: Get the password from POST dict
          """
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        # Passing password_raw=password so password will be hashed
        # Returns a tuple, where first value is BOOL. If True ok, If False no new user is created
        user = auth().store.user_model.create_user(username, password_raw=password)
        if not user[0]: #user is a tuple
            return user[1] # Error message
        else:
            # User is created, let's try redirecting to login page
            try:
                return self.redirect(auth_config()['login_url'], abort=False)
            except (AttributeError, KeyError), e:
                self.abort(403)


class LogoutHandler(BaseHandler):
    """
         Destroy user session and redirect to login
     """

    def get(self):
        auth().unset_session()
        # User is logged out, let's try redirecting to login page
        try:
            self.redirect(auth_config()['login_url'])
        except (AttributeError, KeyError), e:
            return "User is logged out"


class SecureRequestHandler(BaseHandler):
    """
         Only accessible to users that are logged in
     """

    @user_required
    def get(self, **kwargs):
        user = self.auth.get_user_by_session()
        try:
            return "Secure zone for %s <a href='%s'>Logout</a>" % (str(user), auth_config()['logout_url'])
        except (AttributeError, KeyError), e:
            return "Secure zone"

conf = {}
conf['webapp2_extras.sessions'] = {'secret_key': 'my-super-secret-key'}

application = webapp2.WSGIApplication(
    [
        webapp2.Route(r'/auth/login', handler=LoginHandler, name='login'),                                                                                                                                            
        webapp2.Route(r'/auth/logout', handler=LogoutHandler, name='logout'),
        webapp2.Route(r'/secure', handler=SecureRequestHandler, name='secure'),
        webapp2.Route(r'/auth/create', handler=CreateUserHandler, name='create-user'),
    ]
    , debug=True, config=conf)
