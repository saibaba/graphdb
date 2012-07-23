import webapp2
import logging
import os
from google.appengine.ext.webapp import template

from api.graph import Db, Node
import yaml

class Browser(webapp2.RequestHandler):

    def post(self, start_node_id):
        #pathelems = filter(lambda p: len(p) > 0, self.request.path.split("/"))

        #start_node_id = pathelems[len(pathelems)-1]

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
            if 'from' in r:
                s = r['from']
                n1q = dict([ [nv[0].strip(), nv[1].strip() ] for nv in [nv.split("=") for nv in s[s.index("(")+1:s.index(")")].strip().split(",")]])
                for k in n1q:
                    if k == "ref":
                        n1q[k] = True

                n1 = Node.findWithProperties(**n1q)
                if len(n1) > 0:
                    n1 = n1[0]
                    n1.relationships.create(r['type'], n)
                else:
                    self.response.out.write("From node with properties:" + str(n1q) + " not found")
                    return
            if 'to' in r:
                s = r['to']
                n2q = dict([ [nv[0].strip(), nv[1].strip() ] for nv in [nv.split("=") for nv in s[s.index("(")+1:s.index(")")].strip().split(",")]])
                for k in n2q:
                    if k == "ref":
                        n2q[k] = True
                n2 = Node.findWithProperties(**n2q)
                if len(n2) > 0:
                    n2 = n2[0]
                    n.relationships.create(r['type'], n2)
                else:
                    self.response.out.write("To node with properties:" + str(n2q) + " not found")
                    return

        return self.get()

    def get(self, start_node_id):

        #pathelems = filter(lambda p: len(p) > 0, self.request.path.split("/"))
        #start_node_id = pathelems[len(pathelems)-1]
        #logging.info("writing output..." + ";".join(pathelems))        

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

        template_values = { 'node_id': start_node_id, 'start_node_url' : '/browser/' + start_node_id, 'ref': tref }
  
        path = os.path.join(os.path.dirname(__file__), 'browser.html')

        self.response.out.write(template.render(path, template_values))


    def delete(self, node_id):
        
        node = Node.findById(node_id)
        if node is None:
            self.response.status = "404 Not Found"
            self.response.out.write("Node to be deleted not found")
        else:
            node.delete()
            self.response.status = "200 OK"
            self.response.out.write("Node deleted ")
    
application = webapp2.WSGIApplication( 
        [ 
            ('/browser/(.*)', Browser), 
        ] , debug=True)
