from api.graph import Db, Node
import webapp2
import json
import logging
import yaml

class VersionHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(dict(versions=[dict(id="1.0", status="BETA")]))

def reference():
    db = Db()
    return db.reference_node

class NodeAPI(webapp2.RequestHandler):

    def post(self, node_id):

        if node_id == "ref":
            node_id = reference()

        data = self.request.body
        yaml_data = yaml.load(data)

        pl = yaml_data['node']['properties']

        n = Node(**pl)
        rl = yaml_data['node']['relations']

        for r in rl:

            logging.info("**** Adding relation: " + r['type'])

            if 'to_node_id' in r:
                n2 = Node.findById(r['to_node_id'])
                n.relationships.create(r['type'], n2)
                self.response.status = "200 OK"

            elif 'from_node_id' in r:
                n1 = Node.findById(r['from_node_id'])
                n1.relationships.create(r['type'], n)
                self.response.status = "200 OK"

            elif 'from' in r:
                s = r['from']

                n1 = None
                if s == "ref":
                    n1 = reference()
                elif s == "parent":
                    n1 = Node.findById(node_id)
                else:
                    n1q = dict([ [nv[0].strip(), nv[1].strip() ] for nv in [nv.split("=") for nv in s[s.index("(")+1:s.index(")")].strip().split(",")]])
                    n1 = Node.findWithProperties(**n1q)
                    if len(n1) > 0:
                        n1 = n1[0]

                if n1 is not None:
                    logging.info("\t **** Adding relation: from " +  str(n1) + " to " + str(n))
                    n1.relationships.create(r['type'], n)
                    self.response.status = "200 OK"
                else:
                    self.response.status = "404 Not Found"
                    self.response.out.write("From node " + s + " not found")


            elif 'to' in r:
                s = r['to']

                n2 = None
                if s == "ref":
                    n2 = reference()
                elif s == "parent":
                    n2 = Node.findById(node_id)
                else:
                    n2q = dict([ [nv[0].strip(), nv[1].strip() ] for nv in [nv.split("=") for nv in s[s.index("(")+1:s.index(")")].strip().split(",")]])
                    n2 = Node.findWithProperties(**n2q)
                    if len(n2) > 0:
                        n2 = n2[0]
                
                if n2 is not None:
                    n.relationships.create(r['type'], n2)
                    self.response.status = "200 OK"
                else:
                    self.response.status = "404 Not Found"
                    self.response.out.write("To node " + s + " not found")

        self.response.headers['Content-Type']  = "application/json"
        self.response.headers['Location'] = "/graphdb/" + n.id

    def get(self, node_id):

        ref = None
        if node_id == "ref":
            ref = reference()
        else:
            ref = Node.findById(node_id)
            if ref is None:
                self.response.status = "404 Not Found"
                return
                

        logging.info("Starting node to use:" + str(ref))

        tref = { 'attributes' : [] }
        for ap in ref.attributes():
            tref['attributes'].append({'name': ap[0], 'value': ap[1]})

        tref['relationships'] = dict(outgoing=[], incoming=[])
        for r in ref.relationships.outgoing:
            tref['relationships']['outgoing'].append( { 'link' : '/graphdb/' + r.end().id, 'type_name' : r.type.name(), 'attributes' : [] } )
            for rap in r.attributes():
                tref['relationships']['outgoing']['attributes'].append({'name' : rap.name, 'value' : rap.value })
        for r in ref.relationships.incoming:
            tref['relationships']['incoming'].append( { 'link' : '/graphdb/' + r.start().id, 'type_name' : r.type.name(), 'attributes' : [] } )
            for rap in r.attributes():
                tref['relationships']['incoming']['attributes'].append({'name' : rap.name, 'value' : rap.value })

        self.response.headers['Content-Type']  = "application/json"

        self.response.status = "200 OK"
        self.response.out.write(json.dumps(tref))

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
    ('/graphdb/(ref)', NodeAPI),
    ('/graphdb/(.+)', NodeAPI),
  ] , debug=True)
