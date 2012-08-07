from google.appengine.ext import db

from model import entities
import logging
from collections import namedtuple

class _RelationshipsProxy(object):
    DIR_IN = 0
    DIR_OUT = 1
    DIR_BOTH = 2

    def __init__(self, owner_node, direction = DIR_BOTH, type_name = None):
        self.owner_node = owner_node
        self.direction = direction
        self.type_name = type_name

    def create(self, type_name, target_node, **props):
        if self.type_name is not None and self.type_name != type_name:
            raise Exception("This relationship iterator is already prefixed by another type name: " + self.type_name + " and cannot be used to create relationships of type: " + type_name)
        if self.owner_node.tenant != target_node.tenant:
            raise Exception("This relationship can be established between nodes belonging to the same tenant")

        if self.direction == _RelationshipsProxy.DIR_OUT or self.direction == _RelationshipsProxy.DIR_BOTH:
            r = Relationship.create(type_name, self.owner_node, target_node, **props)
        elif self.direction == _RelationshipsProxy.DIR_IN:
            r = Relationship.create(type_name, target_node, self.owner_node, **props)

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
            q1 = self.owner_node.outgoing
            q2 = self.owner_node.incoming
        elif self.direction == _RelationshipsProxy.DIR_IN:
            q1 = self.owner_node.incoming
        elif self.direction == _RelationshipsProxy.DIR_OUT:
            q2 = self.owner_node.outgoing

        if q1 is not None:
            for r in q1:
                yield Relationship(r)

        if q2 is not None:
            for r in q2:
                yield Relationship(r)

    def iter_type_filtered(self):
        logging.info("*** Iterating a rel proxy for rel type: " + self.type_name) 

        q1 = None
        q2 = None

        if self.direction == _RelationshipsProxy.DIR_BOTH:
            q1 = self.owner_node.outgoing
            q2 = self.owner_node.incoming
        elif self.direction == _RelationshipsProxy.DIR_IN:
            q1 = self.owner_node.incoming
        elif self.direction == _RelationshipsProxy.DIR_OUT:
            q1 = self.owner_node.outgoing

        if q1 is not None:
            for r in q1:
                if r.rel_type.key().name() == self.type_name:
                    yield Relationship(r)

        if q2 is not None:
            for r in q2:
                if r.rel_type.key().name() == self.type_name:
                    yield Relationship(r)

class RelationshipType(object):

    def __init__(self, row):
        self.row = row

    def name(self):
        return self.row.key().name()

    @classmethod
    def get(cls, type_name):
        row = entities.RelationshipType.get_or_insert(type_name)
        row.put()
        return RelationshipType(row)

NVPair = namedtuple('NVPair', ['name', 'value'])

class Node(object):


    @classmethod
    def ref(cls, tenant):
        ref_key = "REF_"+tenant
        row  = entities.Node.get(db.Key.from_path('Node', ref_key))
        if row is not None:
            return Node(row)
        else:
            return Node.new(tenant, key_name=ref_key)

    @classmethod
    def new(cls, tenant, key_name = None, **props):
        if key_name is not None:
            row = entities.Node(key_name=key_name, tenant=tenant)
        else:
            row = entities.Node(tenant=tenant)
        row.put()
        n = Node(row)
        n.create_properties(**props)
        return n

    def __init__(self, row):
        self.__dict__['row'] = row
        self.__dict__['relationships'] = _RelationshipsProxy(self)

    def __getattr__(self, n):
        if n == "id":
            return str(self.row.key())
        # or just return self.row and define __get__ on entities.Node to make it a descriptor
        return getattr(self.row, n)

    def __setattr__(self, n, v):
        setattr(self.row, n, v)
        self.row.put()

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __str__(self):
        return "Node with properties:" + ";".join([str((a.name, a.value)) for a in self.attributes()])

    def attributes(self):
        return [NVPair(name=p, value=self[p]) for p in self.row.instance_properties()]

    def create_properties(self, **props):
        for p in props:
            setattr(self.row, p, props[p])
        self.row.put()

    def delete(self):
        self.delete_relations()
        db.delete(self.row.key())
        del self.__dict__['row']

    def delete_relations(self):
        for r in self.relationships:
            r.delete()

    def add_properties(self, propdict):
        for a,v in propdict.items():
            self[a] = v

    def delete_properties(self):
        alist = self.attributes()
        for a in alist:
            delattr(self.row, a.name)
        self.row.put()

    @classmethod
    def findn(cls, tenant, start_key = None, n = 10, page_no = 1):

        # https://developers.google.com/appengine/docs/python/datastore/queries#Query_Cursors

        q = entities.filteredEntity(entities.Node, tenant=tenant)
        qr = q.fetch(1000)

        return [Node(row) for row in qr]

    @classmethod
    def findById(cls, id):
        key = db.Key(id)
        row  = entities.Node.get(key)
        if row is not None: return Node(row)
        else: return None

    @classmethod
    def find(cls, tenant, **props):

        gql = "where tenant = :tenant"

        for a,v in props.items():
            gql += " and " + a + " = :"  + a

        q = entities.Node.gql(gql, tenant=tenant, **props)
        qr = q.fetch(1000)
        nodes = []
        for qri in qr:
            nodes.append(Node(qri))

        return nodes

class Relationship(object):

    def __init__(self, row):
        self.__dict__['row'] = row

    def start(self):
        return Node(self.row.start_node)

    def end(self):
        logging.info("***** GETTING END for start: " + str(self.start().row.key().name() ) )
        return Node(self.row.end_node)

    def __getattr__(self, n):
        if n == "type":
            return RelationshipType(self.row.rel_type)

        return getattr(self.row, n)

    def __setattr__(self, n, v):
        setattr(self.row, n, v)
        self.row.put()

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def attributes(self):
        return [NVPair(name=p, value=self[p]) for p in self.row.instance_properties()]

    def __str__(self):
        alist = self.attributes()
        return "Relationship from " + str(self.start()) + " to " + str(self.end()) + " with name " + self.row.rel_type.key().name() + " and properties: " + ";".join([str((a.name, a.value)) for a in alist])

    def create_properties(self, **props):
        for p in props:
            setattr(self.row, p, props[p])
        self.row.put()

    def delete(self):
        db.delete(self.row.key())
        del self.__dict__['row']

    @classmethod
    def create(cls, type_name, start_node, end_node, **props):
        rt = RelationshipType.get(type_name)
        sn = start_node.row
        en = end_node.row
        row = entities.Relationship(rel_type = rt.row, start_node = sn, end_node = en)
        row.put()
        r = Relationship(row)
        r.create_properties(**props)
        return r

