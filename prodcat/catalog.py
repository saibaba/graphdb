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
        n = r.end()
        break
    else:
        logging.info("*** could not find the catalog root , creating one!!!")
        n = Node(name="CATALOGS_ROOT")
        ref.relationships.create("CATALOGS_REF", n)

    return n

def get_catalog(catalog_name):
    ref = _catalog_root()
    catalog = None

    for r in ref.relationships.outgoing.CATALOG_REL:
        if r.end().name == catalog_name:
            catalog = r.end()
            break

    return catalog

def get_category(parent, category_path, ndx = 0, create_if_missing=False, attributes={}):

    rv = None

    if len(category_path) == 0 or ndx == len(category_path): 
        return parent
    else:

        for r in parent.relationships.outgoing.CATEGORY:
            if r.end().name == category_path[ndx]:
                rv = get_category(r.end(), category_path, ndx+1, create_if_missing, attributes)
                break
        else:
            if create_if_missing:
                logging.info("**** autovivify subcat:" + category_path[ndx])
                n = Node(**attributes)
                n.name = category_path[ndx]
                parent.relationships.outgoing.create("CATEGORY", n)
                rv = get_category(n, category_path, ndx+1, create_if_missing, attributes)
            else:
                rv = None

    return rv

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
                break
        else:
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
            rv = {"message": "3 No catalog found" }
        """

        self.response.out.write(json.dumps(rv))

class Catalog(webapp2.RequestHandler):

    def get(self, catalog_name):
        catalog = get_catalog(catalog_name)
        rv = {}

        if catalog is None:
            self.response.status = "404 Not Found"
            rv = {"message": "2 No catalog with name %s found" % (catalog_name,) }
        else: 
            rv = dict(categories=[], attributes=[])
            
            for r in catalog.relationships.outgoing.CATEGORY:
                rv['categories'].append(r.end().name)
            for a in catalog.attributes():
                rv['attributes'].append(dict(name=a[0],value=a[1]))

        self.response.out.write(json.dumps(rv))

class Category(webapp2.RequestHandler):
   
    def post(self, catalog_name, category_path_string):
        catalog = get_catalog(catalog_name)

        rv = {}
        data = self.request.body
        print data
        attributes = json.loads(data)

        if catalog is None:
            self.response.status = "404 Not Found"
            rv = {"message": "1 No catalog with name %s found" % (catalog_name,) }
        else:
            pathelems = filter(lambda p: len(p) > 0, category_path_string.split("/"))
            logging.info( "Will autovivify: " + category_path_string)
            category = get_category(catalog, pathelems, create_if_missing=True, attributes=attributes)
            self.response.status = "201 Created"
            self.response.headers['Location'] = "/catalogs/"+catalog_name+"/"+category_path_string

            self.response.out.write(json.dumps(rv))


    def get(self, catalog_name, category_path_string):

        catalog = get_catalog(catalog_name)

        rv = {}
        if catalog is None:
            self.response.status = "404 Not Found"
            rv = {"message": "1 No catalog with name %s found" % (catalog_name,) }
        else:
            pathelems = filter(lambda p: len(p) > 0, category_path_string.split("/"))
            category = get_category(catalog, pathelems)
            if category is None:
                self.response.status = "404 Not Found"
                rv = {"message": "No category path with name %s found" % ("/".join(pathelems,)) }
            else:
                self.response.status = "200 OK"
                rv = dict(categories=[], attributes=[])
                for r in category.relationships.outgoing.CATEGORY:
                    rv['categories'].append("/catalogs/%s/%s/%s" % (catalog_name, category_path_string,r.end().name) )
                for a in category.attributes():
                    rv['attributes'].append(dict(name=a[0],value=a[1]))

        self.response.out.write(json.dumps(rv))


application = webapp2.WSGIApplication(
  [
    ('/prodcat/catalogs', Catalogs),
    ('/prodcat/catalogs/([^/]+)', Catalog), 
    ('/prodcat/catalogs/([^/]+)/(.+)', Category), 
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
