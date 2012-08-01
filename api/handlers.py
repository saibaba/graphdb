from api.graph import Db, Node
import json
import logging
import yaml
import re
import os
from google.appengine.ext.webapp import template
import threading
import webapp2
import auth


def reference():
    gdb = Db(auth.get_tenant())
    return gdb.reference_node

class NodeAPI(webapp2.RequestHandler):

    def node_id_to_node(self, node_id):
        n = None
        msg = "Node with id: " + node_id + " does not exist"
        if node_id == "ref":
            n = reference()
        elif node_id.startswith("Node"):
            logging.info("trying spec..............")
            n,msg = self.spec_to_node(None, node_id)
        else:
            n = Node.findById(node_id)
 
        if n is None:
            self.abort(404, msg)

        return n

    def convert_to_yaml(self, data):

        if data is None or len(data) == 0:
            self.abort(400, "Body content is missing or empty")

        yaml_data = None

        try:
            yaml_data = yaml.load(data)
        except Exception, e:
            logging.error(e)
            self.abort(400, "Bad input content, cannot parse yaml")

        return yaml_data

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
        uuid4= re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z', re.I)
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
            n = Node.findWithProperties(auth.get_tenant(), **nq)
            if len(n) == 1:
                n = n[0]
            elif len(n) > 1:
                n = None
                message += "Could not find a unique node nodes with props: "  + str(nq)
            else:
                n = None
                message += "Could not find a node nodes with props: "  + str(nq)

        return (n, message)
        
    def handle_exception(self, exception, debug):
        logging.exception(exception)
        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)
            self.response.write(json.dumps(dict(message=exception.detail)))
        else:
            self.response.set_status(500)

    @auth.user_required
    def put(self, node_id):

        n = self.node_id_to_node(node_id)
        yaml_data = self.convert_to_yaml(self.request.body)

        if 'properties' in yaml_data:
            n.delete_properties()
            n.add_properties(yaml_data['properties'])
        elif 'relations' in yaml_data:
            n.delete_relations()
            self.add_relations(yaml_data['relations'], n, n)
        else:
            self.abort(400, "Expecting properties or relations in the input")

        self.response.status = "204 OK"
        self.response.headers['Location'] = "/graphdb/" + str(n.id)

    def add_relations(self, rl, n, current):
        for r in rl:

            logging.info("**** Adding relation: " + r['type'])

            rpl = r['properties'] if 'properties' in r else {}
            for rpli in rpl:
                if type(rpl[rpli]) != "str":
                    rpl[rpli] = str(rpl[rpli])

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
            else:
                self.abort(404, str(message))

    @auth.user_required
    def post(self, node_id):

        logging.info("**thread " + threading.current_thread().name)
        logging.info("**post data: " + str(self.request.POST))

        current = self.node_id_to_node(node_id)
        yaml_data = None

        if self.request.headers['Content-Type'] == "application/yaml":
            yaml_data = self.convert_to_yaml(self.request.body)
        else:
            if 'yaml' in  self.request.POST:
                yaml_data = self.convert_to_yaml(self.request.POST['yaml'])
            elif 'delete' in self.request.POST:
                return self.delete(node_id)
            else:
                self.abort(400, "Missing input (either submit a form field named yaml or post content-type application/yaml)")

        pl = {}
        rl = []

        n = current

        if 'node' in yaml_data and (yaml_data['node'] is not None) and 'properties' in yaml_data['node']:
            pl = yaml_data['node']['properties']
            for pli in pl:
                if type(pl[pli]) != "str":
                    pl[pli] = str(pl[pli])
            n = Node(auth.get_tenant(), **pl)
            if 'relations' in yaml_data['node']:
                rl = yaml_data['node']['relations']
        elif 'relations' in yaml_data:
            rl = yaml_data['relations']
        elif 'properties' in yaml_data:
            n.add_properties(yaml_data['properties'])
        else:
            self.abort(400, "Expecting node/properties or relations or properties in the POST payload")

        for r in rl:

            logging.info("**** Adding relation: " + r['type'])

            rpl = r['properties'] if 'properties' in r else {}
            for rpli in rpl:
                if type(rpl[rpli]) != "str":
                    rpl[rpli] = str(rpl[rpli])

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
            else:
                self.abort(404, str(message))

        self.response.headers['Content-Type']  = "application/json"
        self.response.headers['Location'] = "/graphdb/" + str(n.id)

        if self.request.headers['Content-Type'] == "application/yaml":
            self.response.status = "201 Created"
        else:
            return self.get(n.id)

    @auth.user_required
    def get(self, node_id):

        ref = self.node_id_to_node(node_id)
        logging.info("Starting node to use:" + str(ref))

        tref = { 'properties' : {}  }
        for ap in ref.attributes():
            tref['properties'][ap[0]] = ap[1]

        tref['relationships'] = dict(outgoing=[], incoming=[])
        for r in ref.relationships.outgoing:
            x = {}
            for rap in r.attributes():
                x[rap[0]] = rap[1]
            tref['relationships']['outgoing'].append( { 'link' : '/graphdb/' + r.end().id, 'type_name' : r.type.name(), 'properties' : x } )
        for r in ref.relationships.incoming:
            x = {}
            for rap in r.attributes():
                x[rap[0]] = rap[1]
            tref['relationships']['incoming'].append( { 'link' : '/graphdb/' + r.start().id, 'type_name' : r.type.name(), 'properties' :   x } )

        self.response.status = "200 OK"

        if self.request.headers['Accept'] == "application/json":
            self.response.headers['Content-Type']  = "application/json"
            self.response.out.write(json.dumps(tref))
        else:
            self.response.headers['Content-Type']  = "text/html"
            template_values = { 'node_id': ref.id, 'start_node_url' : '/graphdb/' + node_id, 'ref': tref }
            path = os.path.join(os.path.dirname(__file__), 'browser.html')
            self.response.out.write(template.render(path, template_values))

    @auth.user_required
    def delete(self, node_id):
                
        node = self.node_id_to_node(node_id)
        node.delete()
        self.response.status = "200 OK"
        self.response.out.write("Node deleted")

class NodeListerAPI(webapp2.RequestHandler):

    @auth.user_required
    def get(self):
        nodes = Node.findn(auth.get_tenant())
        nodes_hash = { 'nodes': [] }

        for n in nodes:
            tref = { 'properties' : {}  , 'node_link' : '/graphdb/' + n.id , 'node_id' : n.id}
            for ap in n.attributes():
                tref['properties'][ap[0]] = ap[1]

            tref['relationships'] = dict(outgoing=[], incoming=[])
            for r in n.relationships.outgoing:
                x = {}
                for rap in r.attributes():
                    x[rap[0]] = rap[1]
                tref['relationships']['outgoing'].append( { 'link' : '/graphdb/' + r.end().id, 'type_name' : r.type.name(), 'properties' : x } )

            for r in n.relationships.incoming:
                x = {}
                for rap in r.attributes():
                    x[rap[0]] = rap[1]
                tref['relationships']['incoming'].append( { 'link' : '/graphdb/' + r.start().id, 'type_name' : r.type.name(), 'properties' :   x } )

            nodes_hash['nodes'].append(tref)

        self.response.status = "200 OK"

        if self.request.headers['Accept'] == "application/json":
            self.response.headers['Content-Type']  = "application/json"
            self.response.out.write(json.dumps(nodes_hash))
        else:
            self.response.headers['Content-Type']  = "text/html"
            template_values = nodes_hash
            path = os.path.join(os.path.dirname(__file__), 'nodelist.html')
            self.response.out.write(template.render(path, template_values))

conf = {}
conf['webapp2_extras.sessions'] = {'secret_key': 'my-super-secret-key'}

application = webapp2.WSGIApplication(
  [
    ('/graphdb/nodes', NodeListerAPI),
    ('/graphdb/(.+)', NodeAPI),
  ] , debug=True, config=conf)
