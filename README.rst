=========================
Graph DB on GAE datastore
=========================

.. raw:: html

  <style> .red {color:red} </style>


.. role:: red

Introduction
============

This is a simple API that provides a Graph DB abstraction over GAE datastore.

Use the API to create nodes and relationships between the nodes. Each node or relationship can have properties as name and value pairs.

Directionality of relationships (incoming or outgoing) is entirely semantic and up to user to define meaning - API allows for traversing in any direction. 

There is always a reference node - eventhough it is not mandatory to use in a relationship graph.
You can use ref (or any) node to create new nodes even if the new ones are not related to it.

It can be used as a `Restful service`_ or as a `Python API`_.



Restful service
===============

Running locally
---------------

Use th following steps to run the restfulapi application locally:

1) Get the code from github

::

   git clone https://github.com/saibaba/graphdb.git


2) Change to the application directory

::

  cd graphdb


3) Launch GAE development

::

   dev_appserver.py .


Registration/Authentication
---------------------------

Before using the restful API, you need to register with a username and password by visiting /auth/login - You need to pass the credentials in each API call.

Reference node's URL: "/graphdb/ref".

Nodes are identified a variety of means as given below in examples.

You can browse through the nodes and create new nodes/relations by starting at: "/graphdb/ref".

**:red:`Make sure to use https in your GAE application as the username/password are in clear.`**

API operations (see the bottom for `Python API`_)
-------------------------------------------------

In the below API operations, the graph nodes can be identified by following means:

* ref
* node_id (the UUID)
* Node(property_name=property_value, ...)  

In the below operations, <node> represents node identification as given above.

Note: Make sure to escape special characters like quotes, '(', and ')' in shell scripts.

Creating a Node
^^^^^^^^^^^^^^^

Create a node (POSTing to either ref or another node identified by <node> below):

**POST /graphdb/<node>**

In request body, include properties/relations in "yaml", for example, as in:

::

  #yaml start
  node:
    properties:
      title: The Matrix
      year: 1999
  #yaml end


Another example
::

  #yaml start
  node:
    properties:
      name: Keanu Reeves
    relations:
      - to: Node(title=The Matrix)
        type: ACTS_IN
        properties:
          name: Neo
  #yaml end

Apart from the format of <node> above, there is one more way to address a node in a relationship: 

* current

This identifies the node to which the content is posted to.

Try above examples in the browser at url: /graphdb/ref.

The same example using curl:

::
  
  curl -X "POST" -H "Content-Type: application/yaml" -H "Accept: application/json" -H "X-Auth-User: demo" -H "X-Auth-Password: demo" http://127.0.0.1:9080/graphdb/ref --data "node: { properties: { name: Keanu Reeves }, relations: [ { to: Node(title=The Matrix), type: ACTS_IN, properties: { name: Neo}  } ] }"


Getting the details of a node
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**GET /graphdb/<node>**

This operation returns the response body with node id including properties, outgoing relations, and incoming relations, for example:

::

  curl -X GET -H "Content-Type: application/yaml" -H "Accept: application/json" -H "X-Auth-User: demo" -H "X-Auth-Password: demo" http://127.0.0.1:9080/graphdb/Node(name=Keanu%20Reeves)

Here is the response:
::
  
  {"relationships": {"outgoing": [{"type_name": "ACTS_IN", "link": "/graphdb/13fed092-2c69-446e-8231-c2d257d9dcff", "properties": {"name": "Neo"}}], "incoming": []}, "properties": {"name": "Keanu Reeves"}}


Updating a node
^^^^^^^^^^^^^^^

Replace a node:

**PUT /graphdb/<node>**

In request body include "yaml" properties and relations (just like in POST) to replace with.
You cannot replace content of ref node - you need to delete individual child nodes.

Adding new properties or relations:

**POST /graphdb/<node>**

In request body include "yaml" just properties and relations (syntax just like in POST) to append to existing properties/relations.
You cannot replace content of ref node - you need to delete individual child nodes.

Removing a node
^^^^^^^^^^^^^^^

**:red:`DELETE /graphdb/<node>`**

This operation deletes the specified node and all of its properties. It also automatically removes all incoming/outgoing relations and their properties.

Delete all nodes
^^^^^^^^^^^^^^^^

**DELETE /graphdb/nodes**

It also deletes the ref node - next time it is required, it will be auto-created.

List all nodes
^^^^^^^^^^^^^^

**GET /graphdb/nodes**

This lists all nodes including their information just like in GET for a single node.

Samples
^^^^^^^

**There are a lot of curl examples in SOCIAL_NETWORK.sh, BLOG.sh, and CATEGORIES.sh in samples/webapi folder.**

TODO
^^^^
a) Post to /graphdb/nodes instead of /graphdb/ref to create new nondes
b) Pagination support for listing


Python API
==========

You just need two files:

* model/entities.py
* api/graph.py

Once they are loaded into GAE environment, you can play with the API directly from the Interactive Console or use in GAE application.


Samples
-------

**Python samples are available in samples/lib folder that you can copy/paste into the console.**

Here is a sample session:

.. image:: https://raw.github.com/saibaba/graphdb/master/movies_ic.png
   :width: 100pt


==========
References
==========
1. http://stackoverflow.com/questions/1630087/how-would-you-design-an-appengine-datastore-for-a-social-site-like-twitter
2. http://neo4j.org/scratchpad/doc/screenshots/
3. http://www.google.com/events/io/2009/sessions/SofterSideofSchemas.html
4. http://www.google.com/events/io/2009/sessions/BuildingScalableComplexApps.html

