#set -x
#set -v

USER="sai2"
PASSWORD="sai2"

COMMON_HEADERS="-v -X POST -H \"Content-Type: application/yaml\" -H \"Accept: application/json\" -H \"X-Auth-User: $USER\" -H \"X-Auth-Password: $PASSWORD\""
URL=http://127.0.0.1:9080/graphdb/ref

echo "Blog graph as in: http://neo4j.org/scratchpad/doc/screenshots/"

echo "Create tags"

eval curl $COMMON_HEADERS $URL --data \"node: { properties: {name: jo4neo } }\"
eval curl $COMMON_HEADERS $URL --data \"node: { properties: {name: welcome } }\"

echo "Create authors"
eval curl $COMMON_HEADERS $URL --data \"node: { properties: {name: Summer } }\"
eval curl $COMMON_HEADERS $URL --data \"node: { properties: {name: Mark } }\"

echo "Create blog entries and apply tags"

eval curl $COMMON_HEADERS $URL --data \"node: { properties: { content: jo4neo makes it easy to provision a graph with data}, relations: [ { to: Node\(name=Summer\), type: author }, { to: Node\(name=jo4neo\), type: hasTag}  ] }\"

eval curl $COMMON_HEADERS $URL --data \"node: { properties: { content: jo4neo provides simple yet useful features}, relations: [ { to: Node\(name=Mark\), type: author }, { to: Node\(name=welcome\), type: hasTag}, { to: Node\(name=jo4neo\), type: hasTag} ] }\"
