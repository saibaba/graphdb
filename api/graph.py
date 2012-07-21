from model import entities
from util import genid
import logging

class _RelationshipsProxy(object):
    DIR_IN = 0
    DIR_OUT = 1
    DIR_BOTH = 2

    def __init__(self, owner_node, direction = DIR_BOTH):
        self.owner_node = owner_node
        self.direction = direction

    def create(self, name, target_node, **props):
        if self.direction == _RelationshipsProxy.DIR_OUT or self.direction == _RelationshipsProxy.DIR_BOTH:
            r = Relationship(name, self.owner_node, target_node, **props)
        elif self.direction == _RelationshipsProxy.DIR_IN:
            r = Relationship(name, target_node, self.owner_node, **props)

        return r

    def outgoing_func(self):
        return _RelationshipsProxy(self.owner_node, _RelationshipsProxy.DIR_OUT)

    def incoming_func(self):
        return _RelationshipsProxy(self.owner_node, _RelationshipsProxy.DIR_IN)

    def __getattr__(self, n):
        if n == "incoming":
            return self.incoming_func()
        elif n == "outgoing":
            return self.outgoing_func()
        else:
            raise AttributeError(n)

    def __iter__(self):

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

class Attribute(object):

    def __init__(self, name, value, owner_id, id = None):

        logging.info( "attribute name = " + name+ " value = "+ str(value) +  " owner_id " + owner_id)

        if id is not None:
            self.id = id
        else:
            qr = Attribute.findByNameAndOwnerId(name, owner_id)
            if qr is not None:
                self.id = qr.id
            else:
                row = entities.Attribute(id=genid(), name=name, value=value, owner_id = owner_id)
                row.put()
                self.id = row.id

    def __getattr__(self, n):
        row = Attribute.findById(self.id)
        return getattr(row, n)

    def set_value(self, v):
        row = Attribute.findById(self.id)
        row.value = v
        row.put()

    def __str__(self):
        return "Property("+self.name + "," + self.value +")"

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

    def __init__(self, id = None, ref=False, **props):

        if id is None:
            row =  entities.Node(id=genid(), ref=ref)
            row.put()
            self.__dict__['id'] =  row.id
            self.create_properties(**props)
        else:
            self.__dict__['id'] =  id

        self.__dict__['relationships'] = _RelationshipsProxy(self)  #NOTE: not persisted

    def __getattr__(self, n):
        return Attribute(n, None, self.id).value

    def __setattr__(self, n, v):
        Attribute(n, None, self.id).set_value(v)

    def __str__(self):
        alist = Attribute.findAllByOwnerId(self.id)
        return "Node with properties:" + ";".join([str((a.name, a.value)) for a in alist])

    def attributes(self):
        alist = Attribute.findAllByOwnerId(self.id)
        return [(a.name, a.value) for a in alist]

    def create_properties(self, **props):
        for p in props:
           Attribute(p, props[p], self.id)

    @classmethod
    def find(cls, **props):
        q = entities.filteredEntity(entities.Node, **props)
        qr = q.fetch(1000)
        return [Node(row.id) for row in qr]

    @classmethod
    def findById(cls, id):
        rv =  Node.find(id=id)
        return rv[0] if (rv is not None and len(rv) > 0) else None

    @classmethod
    def findWithProperties(cls, **props):
        candidates = {}
        first = True
        pc = 0
        for a,v in props.items():
            q = entities.filteredEntity(entities.Attribute, name=a, value=v)
            qr = q.fetch(1000)
            for qr in q:
                if first:
                    candidates[qr.owner_id] = 1
                else:
                    if qr.owner_id in candidates:
                        candidates[qr.owner_id] = candidates[qr.owner_id] + 1

            first = False
            pc += 1

        ids = []
        for nid, c in candidates.items():
            if c == pc: ids.append(nid)

        nodes = [Node(nid) for nid in ids]
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


class Db(object):

    def __init__(self):
        nodes = Node.find(ref=True)
        if len(nodes) == 0:
            self.reference_node = Node(ref=True)
        else:
            self.reference_node = nodes[0]
        logging.info("******** reference node: " + str(self.reference_node) + " with id: " + self.reference_node.id)

if __name__ == "__main__":

    db = Db()

    n0 = Node(name="root", value="B")
    nl = Node(name="left", value="A")
    nr = Node(name="right", value="C")

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
