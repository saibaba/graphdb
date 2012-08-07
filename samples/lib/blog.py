from api.graph import Node

jo4neo = Node.new('BLOG', name="jo4neo")
welcome = Node.new('BLOG', name="welcome")

summer = Node.new('BLOG', name="Summer")
mark = Node.new('BLOG', name="Mark")

post1 = Node.new('BLOG', content="jo4neo makes it easy to provision a graph with data")
post1.relationships.outgoing.create("author", summer)
post1.relationships.outgoing.create("hasTag", jo4neo)

post2 = Node.new('BLOG', content="jo4neo provides simple yet useful features")
post2.relationships.outgoing.create("author", mark)
post2.relationships.outgoing.create("hasTag", welcome)
post2.relationships.outgoing.create("hasTag", jo4neo)


