import sys
sys.path.append("/Users/saibaba.telukunta/tools/google_appengine")
from api.graph import *

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
