import webapp2
import logging
from api.graph import *

class MainPage(webapp2.RequestHandler):

    def get(self):
        logging.info("writing output...")        

        db = Db()

        n0 = Node(name="root", value="B")
        nl = Node(name="left", value="A")
        nr = Node(name="right", value="C")

        n0.relationships.create("LEFT", nl)
        n0.relationships.create("RIGHT", nr)
        nl.relationships.create("NEXT SIBLING", nr)

        data = ""
        data += str(nl)
        data += "\n --- and its relationships are:"
        for r in nl.relationships:
            data += "\n" +  str(r)

        self.response.out.write(data)


application = webapp2.WSGIApplication( [ ('/hi', MainPage), ] , debug=True)
