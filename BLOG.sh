#set -x
#set -v

COMMON_HEADERS="-v -X POST -H \"Content-Type: application/yaml\" -H \"Accept: application/json\" -H \"X-Auth-User: sai1\" -H \"X-Auth-Password: sai1\""
URL=http://127.0.0.1:9080/graphdb/ref

echo "Create tags"

eval curl $COMMON_HEADERS $URL --data \"node: { properties: {name: jo4neo } }\"
eval curl $COMMON_HEADERS $URL --data \"node: { properties: {name: welcome } }\"

echo "Create authors"
eval curl $COMMON_HEADERS $URL --data \"node: { properties: {name: Summer } }\"
eval curl $COMMON_HEADERS $URL --data \"node: { properties: {name: Mark } }\"

echo "Create blog entries and apply tags"

eval curl $COMMON_HEADERS $URL --data \"node: { properties: { content: jo4neo makes it easy to provision a graph with data}, relations: [ { to: Node\(name=Summer\), type: author }, { to: Node\(name=jo4neo\), type: hasTag}  ] }\"

eval curl $COMMON_HEADERS $URL --data \"node: { properties: { content: jo4neo provides simple yet useful features}, relations: [ { to: Node\(name=Mark\), type: author }, { to: Node\(name=welcome\), type: hasTag}, { to: Node\(name=jo4neo\), type: hasTag} ] }\"
