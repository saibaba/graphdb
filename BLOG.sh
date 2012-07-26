echo "Create tags"

curl -v -X "POST" -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/ref --data "node: { properties: {name: jo4neo } }"
curl -v -X "POST" -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/ref --data "node: { properties: {name: welcome } }"

echo "Create authors"

curl -v -X "POST" -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/ref --data "node: { properties: {name: Summer } }"
curl -v -X "POST" -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/ref --data "node: { properties: {name: Mark } }"


echo "Create blog entries and apply tags"

curl -v -X "POST" -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/ref --data "node: { properties: { content: jo4neo makes it easy to provision a graph with data}, relations: [ { to: Node(name=Summer), type: author }, { to: Node(name=welcome), type: hasTag}  ] }"

curl -v -X "POST" -H "Content-Type: application/yaml" -H "Accept: application/json" http://127.0.0.1:9080/graphdb/ref --data "node: { properties: { content: jo4neo provides simple yet useful features}, relations: [ { to: Node(name=Mark), type: author }, { to: Node(name=welcome), type: hasTag}, { to: Node(name=jo4neo), type: hasTag} ] }"
