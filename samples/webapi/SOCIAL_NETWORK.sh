#set -x
#set -v

echo A curl sssion that creates a structure like the one in http://blog.neo4j.org/2010/03/modeling-categories-in-graph-database.html:

USER="social"
PASSWORD="social"

COMMON="-v -X POST -H \"Content-Type: application/yaml\" -H \"Accept: application/json\" -H \"X-Auth-User: $USER\" -H \"X-Auth-Password: $PASSWORD\""
URL=http://127.0.0.1:9080/graphdb/ref

#### delete data from previous run
DELCOMMON="-v -X DELETE -H \"X-Auth-User: $USER\" -H \"X-Auth-Password: $PASSWORD\""
DELURL=http://127.0.0.1:9080/graphdb/nodes
eval curl $DELCOMMON $DELURL
####

echo Create people
eval curl $COMMON $URL --data \"node: { properties: {feat1: a, feat2: b, name: node1 }}\"
eval curl $COMMON $URL --data \"node: { properties: {feat1: a, feat2: b, name: node2 }}\"
eval curl $COMMON $URL --data \"node: { properties: {feat1: a, feat2: d, name: node3 }}\"
eval curl $COMMON $URL --data \"node: { properties: {feat1: c, feat2: d, name: node4 }}\"
eval curl $COMMON $URL --data \"node: { properties: {feat1: a, feat2: b, name: node5 }}\"
eval curl $COMMON $URL --data \"node: { properties: {feat1: a, feat2: b, name: node6 }}\"
eval curl $COMMON $URL --data \"node: { properties: {feat1: a, feat2: b, name: node7 }}\"

####
echo "Add Relationships - be careful,  you might create duplicate relations - rule I followed is relations start from lower numbered nodes to higher ones; also do not use PUT"

URL="http://127.0.0.1:9080/graphdb/Node\(name=node1\)"
eval curl $COMMON $URL --data \"relations: [ { from: Node\(name=node2\), type: KNOWS }, { to: Node\(name=node3\), type: KNOWS}, {from: Node\(name=node5\), type: KNOWS}, {from: Node\(name=node6\), type: KNOWS}  ]\"


URL="http://127.0.0.1:9080/graphdb/Node\(name=node2\)"
eval curl $COMMON $URL --data \"relations: [ { to: Node\(name=node4\), type: KNOWS } ]\"

URL="http://127.0.0.1:9080/graphdb/Node\(name=node3\)"
eval curl $COMMON $URL --data \"relations: [ { to: Node\(name=node5\), type: KNOWS }, { to: Node\(name=node6\), type: KNOWS}]\"


URL="http://127.0.0.1:9080/graphdb/Node\(name=node4\)"
eval curl $COMMON $URL --data \"relations: [ { to: Node\(name=node7\), type: KNOWS } ]\"

URL="http://127.0.0.1:9080/graphdb/Node\(name=node5\)"
eval curl $COMMON $URL --data \"relations: [ { to: Node\(name=node6\), type: KNOWS } ]\"

echo "Done..."
