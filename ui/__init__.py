import webapp2
import logging
from api.graph import *

class Browser(webapp2.RequestHandler):

    def post(self):

        db = Db()
        ref = db.reference_node

        n0 = Node(name="root", value="B")
        ref.relationships.create("ALPHABET_ROOT", n0)

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

    def get(self):

        pathelems = filter(lambda p: len(p) > 0, self.request.path.split("/"))

        start_node_id = pathelems[len(pathelems)-1]

        logging.info("writing output..." + ";".join(pathelems))        

        db = Db()

        ref = Node.findById(start_node_id)
        if ref is None:
            ref = db.reference_node

        logging.info("Starting node to use:" + str(ref))


        html = "<html><head><title>Walk</title></head><body>"
        html += "<h2>Node Attributes:</h2><ul>"
        for ap in ref.attributes():
            html += '<li>' + ap[0]  + ' = ' + ap[1] + '</li>'
        html += "</ul><br />"
        html += "<h2>Outgoing Relations:</h2><ul>"
        for r in ref.relationships.outgoing:
            html += '<li><a href="/browser/' + r.end().id + '">' + r.type.name() + '</a></li>'
            html += "<ul>"
            for rap in r.attributes():
                html += '<li>' + rap[0]  + ' = ' + rap[1] + '</li>'
            html += "</ul>"

        html += "</ul><h2>Incoming Relations:</h2><ul>"
        for r in ref.relationships.incoming:
            html += '<li><a href="/browser/' + r.start().id + '">' + r.type.name() + '</a></li>'
            html += "<ul>"
            for rap in r.attributes():
                html += '<li>' + rap[0]  + ' = ' + rap[1] + '</li>'
            html += "</ul>"

        html += "</ul></body></html>"

        self.response.out.write(html)


application = webapp2.WSGIApplication( [ ('/browser/.*', Browser), ] , debug=True)
