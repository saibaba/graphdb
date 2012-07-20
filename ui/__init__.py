import webapp2
import logging
import os
from google.appengine.ext.webapp import template

from api.graph import *
import yaml

class Test1(webapp2.RequestHandler):
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

class Browser(webapp2.RequestHandler):

    def post(self):
        pathelems = filter(lambda p: len(p) > 0, self.request.path.split("/"))

        start_node_id = pathelems[len(pathelems)-1]

        db = Db()

        node = Node.findById(start_node_id)
        if node is None:
            node = db.reference_node

        """
        node:
          properties:
             name: root
             value: A

          relations:
             
             - to_node_id : 1234
               type: FRIEND
             - to_node_id : 3421
               type: FOE

          {'node': {'properties': { "name": "root", "value" : "A" },
                    'relations': [{'to_node_id': 1234, 'type': 'FRIEND'},
                                                                     {'to_node_id': 3421, 'type': 'FOE'}]
                   }
          }
        """

        logging.info( "***REQ:" +  self.request.POST['yaml'])
        data = yaml.load(self.request.POST['yaml'])
        logging.info( "***YAML:" +  str(data))
        pl = data['node']['properties']

        n = Node(**pl)
        rl = data['node']['relations']

        for r in rl:
            if 'to_node_id' in r:
                n2 = Node.findById(r['to_node_id'])
                n.relationships.create(r['type'], n2)
            if 'from_node_id' in r:
                n1 = Node.findById(r['from_node_id'])
                n1.relationships.create(r['type'], n)

        return self.get()

    def get1(self):

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

        html += "</ul><hr/>" 

        html += '<form method="POST" action="/browser/"' + start_node_id + '"><textarea name="yaml" rows="20" cols="100">#Post your yaml here to create a node as a child</textarea><br/><input type="submit" />'
        
        html += "</body></html>"

        self.response.out.write(html)

    def get(self):

        pathelems = filter(lambda p: len(p) > 0, self.request.path.split("/"))

        start_node_id = pathelems[len(pathelems)-1]

        logging.info("writing output..." + ";".join(pathelems))        

        db = Db()

        ref = Node.findById(start_node_id)
        if ref is None:
            ref = db.reference_node

        logging.info("Starting node to use:" + str(ref))

        tref = { 'attributes' : [] }
        for ap in ref.attributes():
            tref['attributes'].append({'name': ap[0], 'value': ap[1]})

        tref['relationships'] = dict(outgoing=[], incoming=[])
        for r in ref.relationships.outgoing:
            tref['relationships']['outgoing'].append( { 'end_url' : '/browser/' + r.end().id, 'type_name' : r.type.name(), 'attributes' : [] } )
            for rap in r.attributes():
                tref['relationships']['outgoing']['attributes'].append({'name' : rap.name, 'value' : rap.value })
        for r in ref.relationships.incoming:
            tref['relationships']['incoming'].append( { 'start_url' : '/browser/' + r.start().id, 'type_name' : r.type.name(), 'attributes' : [] } )
            for rap in r.attributes():
                tref['relationships']['incoming']['attributes'].append({'name' : rap.name, 'value' : rap.value })

        template_values = { 'start_node_url' : '/browser/' + start_node_id, 'ref': tref }
  
        path = os.path.join(os.path.dirname(__file__), 'browser.html')

        self.response.out.write(template.render(path, template_values))

application = webapp2.WSGIApplication( [ ('/browser/test1', Test1), ('/browser/.*', Browser), ] , debug=True)
