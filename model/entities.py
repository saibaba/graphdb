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

class ModelBase(db.Model):
    id = db.StringProperty(required=True)
    creation_date = db.DateTimeProperty(auto_now_add=True)
    created_by = db.StringProperty()
    lastupdate_date = db.DateTimeProperty(auto_now=True)
    lastupdated_by = db.StringProperty()

class Attribute(ModelBase):
    name = db.StringProperty(required=True)
    value = db.StringProperty(required=True)
    owner_id = db.StringProperty(required=True)  #node.id or relationship.id

class Node(ModelBase):
    ref = db.BooleanProperty(default=False)

class RelationshipType(ModelBase):
    name = db.StringProperty(required=True)

class Relationship(ModelBase):
    type_id = db.StringProperty(required=True)
    start_node_id = db.StringProperty(required=True)
    end_node_id = db.StringProperty(required=True)

def filteredEntity(entity, **filter):
    eq = entity.all()
    for n,v in filter.items():
        eq.filter(n + " = ", v)

    return eq
