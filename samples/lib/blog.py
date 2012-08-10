from api.graph import Node

tenant='myblog'

jo4neo = Node.new(tenant, name="jo4neo")
welcome = Node.new(tenant, name="welcome")

summer = Node.new(tenant, name="Summer")
mark = Node.new(tenant, name="Mark")

post1 = Node.new(tenant, content="jo4neo makes it easy to provision a graph with data")
post1.relationships.outgoing.create("author", summer)
post1.relationships.outgoing.create("hasTag", jo4neo)

post2 = Node.new(tenant, content="jo4neo provides simple yet useful features")
post2.relationships.outgoing.create("author", mark)
post2.relationships.outgoing.create("hasTag", welcome)
post2.relationships.outgoing.create("hasTag", jo4neo)

c = 0
for r in post2.relationships.outgoing.hasTag:
    c+=1

assert c == 2
