from google.appengine.ext import db

def to_dict(model):
    nvpairs = []
    for p in model.properties():
        attr = getattr(model, p)
        if attr == None:
            attr = None
        else:
            attr = unicode(attr)
        nvpairs.append( (p, attr) )
                                                         
    return dict(nvpairs)

class ModelBase(db.Expando):
    creation_date = db.DateTimeProperty(auto_now_add=True)
    created_by = db.StringProperty()
    lastupdate_date = db.DateTimeProperty(auto_now=True)
    lastupdated_by = db.StringProperty()

class Node(ModelBase):
    tenant = db.StringProperty(required=True)

class RelationshipType(ModelBase):
    pass

class Relationship(ModelBase):
    rel_type = db.ReferenceProperty(RelationshipType, collection_name = 'relations', required = True)
    start_node = db.ReferenceProperty(Node, collection_name='outgoing', required  = True)
    end_node = db.ReferenceProperty(Node, collection_name='incoming', required  = True)

def filteredEntity(entity, **filter):
    eq = entity.all()
    for n,v in filter.items():
        eq.filter(n + " = ", v)

    return eq

def delete(entity, **filter):
    eq = filteredEntity(entity, **filter)
    rows = eq.fetch(1000)
    for row in rows:
        row.delete()

