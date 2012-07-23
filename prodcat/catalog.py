from api.graph import Db, Node
import webapp2
import json
import logging

class VersionHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(dict(versions=[dict(id="1.0", status="BETA")]))

def _catalog_root():
    db = Db()
    ref = db.reference_node
    n = None
    for r in ref.relationships.outgoing['CATALOGS_REF']:
        n =  r.end()
        break
    else:
        logging.info("*** could not find the catalog root , creating one!!!")
        n = Node(name="CATALOGS_ROOT")
        ref.relationships.create("CATALOGS_REF", n)

    return n

class Catalogs(webapp2.RequestHandler):

    def post(self):

        ref = _catalog_root()

        data = self.request.body
        req_json = json.loads(data)
        catalog_name = req_json['catalog_name']

        self.response.headers['Content-Type']  = "application/json"
        self.response.headers['Location'] = "/catalog/" + str(catalog_name)

        for r in ref.relationships.outgoing.CATALOG_REL:
            if r.end().name == catalog_name:
                self.response.status = "409 Conflict"
                self.response.out.write("Catalog already created!")
                return

        ref.relationships.create("CATALOG_REL" , Node(name=catalog_name))
        self.response.status = "201 Created"
        self.response.out.write("Catalog created!")

    def get(self):
        ref = _catalog_root()

        logging.info(ref)

        self.response.headers['Content-Type']  = "application/json"

        rv = {'catalogs' : [] }

        self.response.status = "200 OK"

        for r in ref.relationships.outgoing.CATALOG_REL:
            rv['catalogs'].append(r.end().name)
        """
        else:
            self.response.status = "404 Not Found"
            rv = {"message": "No catalog found" }
        """

        self.response.out.write(json.dumps(rv))

class Catalog(webapp2.RequestHandler):

    def get(self, name=None):
        #ref = _catalog_root()
        if name is None:
            self.response.out.write("Will list all")
        else:
            self.response.out.write("Will list " + name)

application = webapp2.WSGIApplication(
  [
    ('/prodcat/catalogs', Catalogs),
    ('/prodcat/catalogs/(.+)', Catalog), 
  ] , debug=True)

"""
class Category(object):

    def POST(self):
        data = web.data()
        print data
        req_json = json.loads(data)
                                        rv = PaymentMethod.create(req_json)
                                                

                                                        print "return value:", rv

                                                                d = rv.value
                                                                        content = _write(d)

                                                                                if content is not None:
                                                                                                return content

                                                                                                def PUT(self):
                                                                                                            data = web.data()
                                                                                                                    req_json = json.loads(data)
                                                                                                                            pm = PaymentMethod.find(req_json)
                                                                                                                                    print "Find result:", pm
                                                                                                                                            d = pm.value
                                                                                                                                                    print "Find value:", d
                                                                                                                                                            rv = d.update(req_json)
                                                                                                                                                                    d = rv.value
                                                                                                                                                                            print "update value:", d
                                                                                                                                                                                    content = _write(d)
                                                                                                                                                                                            if content is not None:
                                                                                                                                                                                                            return content
"""
