from api.graph import Db, Node
import webapp2
import json
import logging
import yaml
import re

class VersionHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(dict(versions=[dict(id="1.0", status="BETA")]))

def reference():
    gdb = Db()
    return gdb.reference_node

class NodeAPI(webapp2.RequestHandler):

    def node_id_to_node(self, node_id):
        if node_id == "ref":
            node_id = reference()

        n = Node.findById(node_id)

        if n is None:
            self.abort(404, "Node with id: " + node_id + " does not exist")

        return n

    def get_input_as_yaml(self):
        data = self.request.body

        if data is None or len(data) == 0:
            self.abort(400, "Body content is missing or empty")

        yaml_data = None

        try:
            yaml_data = yaml.load(data)
        except Exception, e:
            logging.error(e)
            self.abort(400, "Bad input content, cannot parse yaml")

        return yaml_data


    def is_uuid4(self, spec):
        #http://stackoverflow.com/questions/11384589/what-is-the-correct-regex-for-matching-values-generated-by-uuid-uuid4-hex
        uuid4= re.compile('[0-9a-f]{8}-[]{4}-[]{4}-[]{4}-[]{12}\Z', re.I)
        return uuid4.match(spec) is not None

    def spec_to_node(self, current, spec):

        n = None
        message = ""

        if spec == "ref":
            n = reference()
        elif spec == "current":
            n = current
        elif self.is_uuid4(spec):
            n = Node.findById(spec)
            if n is None:
                message += "Node with id: " + spec + " does not exist"
        else:
            nq = dict([ [nv[0].strip(), nv[1].strip() ] for nv in [nv.split("=") for nv in spec[spec.index("(")+1:spec.index(")")].strip().split(",")]])
            n = Node.findWithProperties(**nq)
            if len(n) == 1:
                n = n[0]
            elif len(n) > 1:
                message += "Could not find a unique node nodes with props: "  + str(nq)
            else:
                message += "Could not find a node nodes with props: "  + str(nq)

        return (n, message)
        
    def handle_exception(self, exception, debug):
        logging.exception(exception)
        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)
            self.response.write(json.dumps(dict(message=exception.detail)))
        else:    
            self.response.set_status(500)

    def put(self, node_id):

        n = self.node_id_to_node(node_id)
        yaml_data = self.get_input_as_yaml()

        if 'properties' in yaml_data:
            n.delete_properties()
            n.add_properties(yaml_data['properties'])
        else:
            self.abort(400, "Expecting properties in the input")

        self.response.status = "204 OK"
        self.response.headers['Location'] = "/graphdb/" + str(n.id)

    def post(self, node_id):

        current = self.node_id_to_node(node_id)
        yaml_data = self.get_input_as_yaml()

        pl = {}
        rl = []

        n = None

        if 'node' in yaml_data:
            pl = yaml_data['node']['properties']
            n = Node(**pl)
            if 'relations' in yaml_data['node']:
                rl = yaml_data['node']['relations']
        elif 'relations' in yaml_data:
            rl = yaml_data['relations']
        elif 'properties' in yaml_data:
            n.add_properties(yaml_data['properties'])

        for r in rl:

            logging.info("**** Adding relation: " + r['type'])

            rpl = {}
            if 'properties' in r:
                rpl = r['properties']

            n1 = None
            n2 = None

            message = ""

            if 'from' in r:
                s = r['from']
                n1, msg =  self.spec_to_node(current, s)
                message += msg
                n2 = n

            elif 'to' in r:
                s = r['to']
                n2, msg =  self.spec_to_node(current, s)
                message += msg
                n1 = n
        
            if n1 is not None and n2 is not None:
                n1.relationships.create(r['type'], n2, **rpl)
                self.response.status = "200 OK"
            else:
                self.abort(404, str(message))

        self.response.headers['Content-Type']  = "application/json"
        self.response.headers['Location'] = "/graphdb/" + str(n.id)


    def get(self, node_id):

        ref = self.node_id_to_node(node_id)
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
                
        node = self.node_id_to_node(node_id)
        node.delete()
        self.response.status = "200 OK"
        self.response.out.write("Node deleted")

application = webapp2.WSGIApplication(
  [
    ('/graphdb/(ref)', NodeAPI),
    ('/graphdb/(.+)', NodeAPI),
  ] , debug=True)
