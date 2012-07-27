####
echo A curl sssion that creates a structure like the one in http://blog.neo4j.org/2010/03/modeling-categories-in-graph-database.html:

echo Create people
curl -v -X "POST" -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/ref --data "node: { properties: {feat1: a, feat2: b, name: node1 }}"
curl -v -X "POST" -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/ref --data "node: { properties: {feat1: a, feat2: b, name: node2 }}"
curl -v -X "POST" -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/ref --data "node: { properties: {feat1: a, feat2: d, name: node3 }}"
curl -v -X "POST" -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/ref --data "node: { properties: {feat1: c, feat2: d, name: node4 }}"
curl -v -X "POST" -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/ref --data "node: { properties: {feat1: a, feat2: b, name: node5 }}"
curl -v -X "POST" -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/ref --data "node: { properties: {feat1: a, feat2: b, name: node6 }}"
curl -v -X "POST" -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/ref --data "node: { properties: {feat1: a, feat2: b, name: node7 }}"

####
echo "Add Relationships (be careful,  you might create duplicate relations - rule I followed is relations start from lower numbered nodes to higher ones; also do not use PUT)"

curl -v -X POST -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/Node\(name=node1\) --data "relations: [ { from: Node(name=node2), type: KNOWS }, { to: Node(name=node3), type: KNOWS}, {from: Node(name=node5), type: KNOWS}, {from: Node(name=node6), type: KNOWS}  ]"
curl -v -X POST -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/Node\(name=node2\) --data "relations: [ { to: Node(name=node4), type: KNOWS } ]"
curl -v -X POST -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/Node\(name=node3\) --data "relations: [ { to: Node(name=node5), type: KNOWS }, { to: Node(name=node6), type: KNOWS}]"
curl -v -X POST -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/Node\(name=node4\) --data "relations: [ { to: Node(name=node7), type: KNOWS } ]"
curl -v -X POST -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/Node\(name=node5\) --data "relations: [ { to: Node(name=node6), type: KNOWS } ]"

echo "Done..."
