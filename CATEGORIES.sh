#set -x
#set -v

USER="demo"
PASSWORD="demo"

COMMON="-v -X POST -H \"Content-Type: application/yaml\" -H \"Accept: application/json\" -H \"X-Auth-User: $USER\" -H \"X-Auth-Password: $PASSWORD\""
BASE_URL=http://127.0.0.1:9080/graphdb

echo "A curl session that creates a product catalog structure similar to the one in http://blog.neo4j.org/2010/03/modeling-categories-in-graph-database.html:"
####
echo "Create ATTRIBUTE_REF"

eval curl $COMMON $BASE_URL/ref --data \"node: { properties: {name: ATTRIBUTE_REF }, relations: [ { from: ref, type: ATTRIBUTE_ROOT} ] }\"

echo "Create attributes"

eval curl $COMMON $BASE_URL/ref --data \"node: { properties: {Name: Name }, relations: [ { from: Node\(name=ATTRIBUTE_REF\), type: ATTRIBUTE_TYPE } ] }\"
eval curl $COMMON $BASE_URL/ref --data \"node: { properties: {Name: Currency, Unit: USD }, relations: [ { from: Node\(name=ATTRIBUTE_REF\), type: ATTRIBUTE_TYPE } ] }\"
eval curl $COMMON $BASE_URL/ref --data \"node: { properties: {Name: Frequency, Unit: MHz }, relations: [ { from: Node\(name=ATTRIBUTE_REF\), type: ATTRIBUTE_TYPE } ] }\"
eval curl $COMMON $BASE_URL/ref --data \"node: { properties: {Name: Length, Unit: inch }, relations: [ { from: Node\(name=ATTRIBUTE_REF\), type: ATTRIBUTE_TYPE } ] }\"
eval curl $COMMON $BASE_URL/ref --data \"node: { properties: {Name: Count, Unit: pcs. }, relations: [ { from: Node\(name=ATTRIBUTE_REF\), type: ATTRIBUTE_TYPE } ] }\"
eval curl $COMMON $BASE_URL/ref --data \"node: { properties: {Name: Weight, Unit: Kg }, relations: [ { from: Node\(name=ATTRIBUTE_REF\), type: ATTRIBUTE_TYPE } ] }\"


####
echo "Create Products/Category Root Node"

eval curl $COMMON $BASE_URL/ref --data \"node: { properties: {name: Products }, relations: [ { from: ref, type: CATEGORY_ROOT } ] }\"

 
####

echo "Create SUBCATEGORIES"

eval curl $COMMON $BASE_URL/ref --data \"node: { properties: {Name: Electronics }, relations: [ { from: Node\(name=Products\),    type: SUBCATEGORY } ] }\"
eval curl $COMMON $BASE_URL/ref --data \"node: { properties: {Name: Computers   }, relations: [ { from: Node\(Name=Electronics\), type: SUBCATEGORY } ] }\"
eval curl $COMMON $BASE_URL/ref --data \"node: { properties: {Name: Desktops    }, relations: [ { from: Node\(Name=Computers\),   type: SUBCATEGORY } ] }\"
eval curl $COMMON $BASE_URL/ref --data \"node: { properties: {Name: Laptops     }, relations: [ { from: Node\(Name=Computers\),   type: SUBCATEGORY } ] }\"
eval curl $COMMON $BASE_URL/ref --data \"node: { properties: {Name: Cameras     }, relations: [ { from: Node\(Name=Electronics\), type: SUBCATEGORY } ] }\"

####

echo "Add Atributes to Electornics"

eval curl $COMMON "$BASE_URL/Node\(Name=Electronics\)" --data \"relations: [ { to: Node\(Name=Name\), type: ATTRIBUTE, properties: { Name: Name, Required: True } }, { to: Node\(Name=Currency\), type: ATTRIBUTE, properties: { Name: Price, Required: True } } , { to: Node\(Name=Weight\), type: ATTRIBUTE, properties: { Name: Weight, Required: True } } ]\"

####
echo "Add Attributes to Computers"

eval curl $COMMON "$BASE_URL/Node\(Name=Computers\)" --data \"relations: [ { to: Node\(Name=Weight\), type: ATTRIBUTE, properties: { Name: Shipping Weight, Required: True } }, { to: Node\(Name=Frequency\), type: ATTRIBUTE, properties: { Name: CPU Frequency, Required: True } } ]\"

####
echo "Add Attributes to Desktops"
eval curl $COMMON "$BASE_URL/Node\(Name=Desktops\)" --data \"relations: [ { to: Node\(Name=Count\), type: ATTRIBUTE, properties: { Name: Expansion slots, DefaultValue: 4 } } ]\"

####
echo "Add attributes to Laptops"

eval curl $COMMON "$BASE_URL/Node\(Name=Laptops\)"  --data \"relations: [ { to: Node\(Name=Length\), type: ATTRIBUTE, properties: { Name: Display Size, DefaultValue: 15.0 } } ]\"

####
echo "Add Product Items"

eval curl $COMMON "$BASE_URL/Node\(Name=Desktops\)" --data \"node: { properties: {CPU Frequency: 3000, Name: Dell Desktop, Price: 890.0, Shipping Weight: 22.3, Weight: 17.1 }, relations: [ { from: current, type: PRODUCT } ] }\"

eval curl $COMMON "$BASE_URL/Node\(Name=Laptops\)" --data \"node: { properties: {CPU Frequency: 2000, Name: HP Laptop, Price: 1200.0, Shipping Weight: 6.3, Weight: 3.5 }, relations: [ { from: current, type: PRODUCT } ] }\"

echo "\n\nDone..."
