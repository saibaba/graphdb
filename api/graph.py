from model import entities
from util import genid
import logging

class _RelationshipsProxy(object):
    DIR_IN = 0
    DIR_OUT = 1
    DIR_BOTH = 2

    def __init__(self, owner_node, direction = DIR_BOTH, type_name = None):
        self.owner_node = owner_node
        self.direction = direction
        self.type_name = type_name

    def create(self, name, target_node, **props):
        if self.type_name is not None and self.type_name != name:
            raise Exception("This relationship iterator is already prefixed by another type name: " + self.type_name + " and cannot be used to create relationships of type: " + name)

        if self.direction == _RelationshipsProxy.DIR_OUT or self.direction == _RelationshipsProxy.DIR_BOTH:
            r = Relationship(name, self.owner_node, target_node, **props)
        elif self.direction == _RelationshipsProxy.DIR_IN:
            r = Relationship(name, target_node, self.owner_node, **props)

        return r

    def outgoing_func(self):
        return _RelationshipsProxy(self.owner_node, _RelationshipsProxy.DIR_OUT, self.type_name)

    def incoming_func(self):
        return _RelationshipsProxy(self.owner_node, _RelationshipsProxy.DIR_IN, self.type_name)

    def __getattr__(self, n):
        if n == "incoming":
            return self.incoming_func()
        elif n == "outgoing":
            return self.outgoing_func()
        else:
            logging.info("*** Returning a rel proxy for rel type: " + n)
            # return relationships of type.name() = n
            #raise AttributeError(n)
            return _RelationshipsProxy(self.owner_node, self.direction, n)

    def __getitem__(self, key):
       return _RelationshipsProxy(self.owner_node, self.direction, key)

    def __iter__(self):
        if self.type_name is not None:
            return iter(self.iter_type_filtered())
        else:
            return iter(self.iter_generic())

    def iter_generic(self):

        q1 = None
        q2 = None

        if self.direction == _RelationshipsProxy.DIR_BOTH:
            q1 = entities.filteredEntity(entities.Relationship, start_node_id = self.owner_node.id)
            q2 = entities.filteredEntity(entities.Relationship, end_node_id = self.owner_node.id)
        elif self.direction == _RelationshipsProxy.DIR_IN:
            q1 = entities.filteredEntity(entities.Relationship, end_node_id = self.owner_node.id)
        elif self.direction == _RelationshipsProxy.DIR_OUT:
            q1 = entities.filteredEntity(entities.Relationship, start_node_id = self.owner_node.id)

        if q1 is not None:
            qr = q1.fetch(1000)
            for r in qr:
                yield Relationship(RelationshipType(id=r.type_id).name(), Node.findById(r.start_node_id), Node.findById(r.end_node_id), id=r.id)

        if q2 is not None:
            qr = q2.fetch(1000)
            for r in qr:
                yield Relationship(RelationshipType(id=r.type_id).name(), Node.findById(r.start_node_id), Node.findById(r.end_node_id), id=r.id)

    def iter_type_filtered(self):
        logging.info("*** Iterating a rel proxy for rel type: " + self.type_name) 

        q1 = None
        q2 = None

        type_id = RelationshipType(type_name=self.type_name).id

        if self.direction == _RelationshipsProxy.DIR_BOTH:
            q1 = entities.filteredEntity(entities.Relationship, start_node_id = self.owner_node.id, type_id = type_id)
            q2 = entities.filteredEntity(entities.Relationship, end_node_id = self.owner_node.id, type_id = type_id)
        elif self.direction == _RelationshipsProxy.DIR_IN:
            q1 = entities.filteredEntity(entities.Relationship, end_node_id = self.owner_node.id, type_id = type_id)
        elif self.direction == _RelationshipsProxy.DIR_OUT:
            q1 = entities.filteredEntity(entities.Relationship, start_node_id = self.owner_node.id, type_id = type_id)

        if q1 is not None:
            qr = q1.fetch(1000)
            for r in qr:
                yield Relationship(RelationshipType(id=r.type_id).name(), Node.findById(r.start_node_id), Node.findById(r.end_node_id), id=r.id)

        if q2 is not None:
            qr = q2.fetch(1000)
            for r in qr:
                yield Relationship(RelationshipType(id=r.type_id).name(), Node.findById(r.start_node_id), Node.findById(r.end_node_id), id=r.id)

class Attribute(object):

    def __init__(self, name, value, owner_id, id = None):

        logging.info( "attribute name = " + name+ " value = "+ str(value) +  " owner_id " + owner_id)

        row = None

        if id is not None:
            self.id = id
        else:
            qr = Attribute.findByNameAndOwnerId(name, owner_id)
            if qr is not None:
                self.id = qr.id
            else:
                row = entities.Attribute(id=genid(), name=name, value=value, owner_id = owner_id)
                self.id = row.id

        if row is not None:
            if value is not None:
                row.value  = value
            row.put()

    def __getattr__(self, n):
        row = Attribute.findById(self.id)
        return getattr(row, n)

    def set_value(self, v):
        row = Attribute.findById(self.id)
        row.value = v
        row.put()

    def __str__(self):
        return "Property("+self.name + "," + self.value +")"

    def delete(self):
        entities.delete(entities.Attribute, id=self.id) 

    @classmethod
    def findById(cls, id):
        q = entities.filteredEntity(entities.Attribute, id=id)
        qr = q.fetch(1000)
        if len(qr) > 0:
            return qr[0]
        else:
            return None

    @classmethod
    def findByNameAndOwnerId(cls, name, id):
        q = entities.filteredEntity(entities.Attribute, name=name, owner_id=id)
        qr = q.fetch(1000)
        if len(qr) > 0:
            return qr[0]
        else:
            return None

    @classmethod
    def findAllByOwnerId(cls, id):
        q = entities.filteredEntity(entities.Attribute, owner_id=id)
        qr = q.fetch(1000)
        return qr

class RelationshipType(object):

    def __init__(self, type_name = None, id=None):
        logging.info( "typename is    "+ str(type_name))
        q = None
        if id is not None:
            q = entities.filteredEntity(entities.RelationshipType, id=id)
        else:
            q = entities.filteredEntity(entities.RelationshipType, name=type_name)

        qr = q.fetch(1000)
        if len(qr) > 0:
            self.id = qr[0].id
            self.type_name = qr[0].name
        else:
            row  = entities.RelationshipType(name=type_name, id=genid())
            row.put()
            self.id = row.id
            self.type_name = type_name

    def name(self):
        return self.type_name

    @classmethod
    def create(cls, type_name):
        return RelationshipType(type_name)

    def __getattr__(self, n):
        q = entities.filteredEntity(entities.RelationshipType, id=self.id)
        qr = q.fetch(1000)
        row = qr[0]
        return getattr(row, n)

class Base(object):

    def __init__(self, **props):
        self.__dict__['id'] = genid()
        Base.create_properties(self.id, **props)

    @classmethod
    def create_properties(cls, owner_id, **props):
        for p in props:
           Attribute(p, props[p], owner_id)


    def __getattr__(self, n):
        return Attribute(n, None, self.id).value

    def __setattr__(self, n, v):
        Attribute(n, None, self.id).set_value(v)

    def __str__(self):
        alist = Attribute.findAllByOwnerId(self.id)
        return ";".join([str((a.name, a.value)) for a in alist])

class Node(object):

    def __init__(self, tenant, id = None, ref=False, **props):

        if id is None:
            row =  entities.Node(id=genid(), ref=ref, tenant=tenant)
            row.put()
            self.__dict__['id'] =  row.id
            self.create_properties(**props)
        else:
            self.__dict__['id'] = id

        self.__dict__['relationships'] = _RelationshipsProxy(self)  #NOTE: not persisted

    def __getattr__(self, n):
        return Attribute(n, None, self.id).value

    def __setattr__(self, n, v):
        Attribute(n, v, self.id)    #.set_value(v)

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __str__(self):
        alist = Attribute.findAllByOwnerId(self.id)
        return "Node with properties:" + ";".join([str((a.name, a.value)) for a in alist])

    def attributes(self):
        alist = Attribute.findAllByOwnerId(self.id)
        return [(a.name, a.value) for a in alist]

    def create_properties(self, **props):
        for p in props:
           Attribute(p, props[p], self.id)

    def delete(self):
        self.delete_properties()
        self.delete_relations()
        entities.delete(entities.Node, id=self.id)

    def delete_relations(self):
        for r in self.relationships:
            r.delete()

    def add_properties(self, propdict):
        for a,v in propdict.items():
            self[a] = v

    def delete_properties(self):
        alist = Attribute.findAllByOwnerId(self.id)
        for a in alist:
            a.delete()

    @classmethod
    def find(cls, tenant, **props):
        q = entities.filteredEntity(entities.Node, tenant=tenant, **props)
        qr = q.fetch(1000)
        return [Node(tenant, id = row.id) for row in qr]

    @classmethod
    def findn(cls, tenant, n = 10, page_no = 1):

        # https://developers.google.com/appengine/docs/python/datastore/queries#Query_Cursors

        q = entities.filteredEntity(entities.Node, tenant=tenant)
        qr = q.fetch(1000)

        return [Node(tenant, id = row.id) for row in qr]

    @classmethod
    def findById(cls, id):
        q = entities.filteredEntity(entities.Node, id = id)
        qr = q.fetch(1)
        if len(qr) > 0:
            return Node(qr[0].tenant, id=qr[0].id)
        else:
            return None

    @classmethod
    def findWithProperties(cls, tenant, **props):
        candidates = {}
        first = True
        pc = 0
        for a,v in props.items():
            q = entities.filteredEntity(entities.Attribute, name=a, value=v)
            qr = q.fetch(1000)
            for qri in qr:
                if first:
                    candidates[qri.owner_id] = 1
                else:
                    if qri.owner_id in candidates:
                        candidates[qri.owner_id] = candidates[qri.owner_id] + 1

            first = False
            pc += 1

        ids = []
        for nid, c in candidates.items():
            if c == pc: ids.append(nid)

        nodes = []
        for nid in ids:
            n = Node.findById(nid)
            if n is not None and n.tenant == tenant:
                nodes.append(n)
        return nodes

class Relationship(object):

    def __init__(self, name, start, end, id  = None, **props):

        self.__dict__['type'] = RelationshipType.create(name)

        if id is None:
            row = entities.Relationship(id=genid(), name=self.type, start_node_id = start.id, end_node_id = end.id, type_id = self.type.id)
            row.put()
            self.__dict__['id'] = row.id
            self.create_properties(**props)
        else:
            self.__dict__['id'] = id

        self.__dict__['start_node'] = start
        self.__dict__['end_node'] = end


    def start(self):
        return self.start_node

    def end(self):
        return self.end_node

    def __getattr__(self, n):
        return Attribute(n, None, self.id).value

    def __setattr__(self, n, v):
        Attribute(n, None, self.id).set_value(v)

    def attributes(self):
        alist = Attribute.findAllByOwnerId(self.id)
        return [(a.name, a.value) for a in alist]

    def __str__(self):
        logging.info("***** stringify start: " + str(self.start()))
        alist = Attribute.findAllByOwnerId(self.id)
        return "Relationship from " + str(self.start()) + " to " + str(self.end()) + " with name " + self.type.name() + " and properties: " + ";".join([str((a.name, a.value)) for a in alist])

    def create_properties(self, **props):
        for p in props:
           Attribute(p, props[p], self.id)


    def delete(self):
        alist = Attribute.findAllByOwnerId(self.id)
        for a in alist:
            a.delete()
        entities.delete(entities.Relationship, id=self.id) 

class Db(object):

    def __init__(self, tenant):
        nodes = Node.find(tenant, ref=True)
        if len(nodes) == 0:
            self.reference_node = Node(tenant, ref=True)
        else:
            self.reference_node = nodes[0]
        logging.info("******** reference node: " + str(self.reference_node) + " with id: " + self.reference_node.id)

if __name__ == "__main__":

    mydb = Db()

    print mydb.reference()

    n0 = Node("test1", name="root", value="B")
    nl = Node("test1", name="left", value="A")
    nr = Node("test1", name="right", value="C")

    n0.relationships.create("LEFT", nl)
    n0.relationships.create("RIGHT", nr)
    nl.relationships.create("NEXT SIBLING", nr)

    print nl, " --- and its relationships are:"
    for r in nl.relationships:
        print r

    print " --- outgoing only are :"
    for r in nl.relationships.outgoing:
        print r

    print " --- incoming only are :"
    for r in nl.relationships.incoming:
        print r
