# PooKeeper

Python + ZooKeeper = PooKeeper

A Python+[Twisted](https://twistedmatrix.com/trac/) implementation of [ZooKeeper](http://zookeeper.apache.org/).

The purpose of this project is academic (as in 'for my personal understanding', not as in 'for a grade):
recreate all features of ZooKeeper to appreciate the intricacies of it.
All tooling decisions have been made to decrease the time spent writing the service in order to spend more time testing its correctness.
For example, Twisted was chosen so that the server state, the znodes, are maintained in one process.
Choosing a framework such as [Flask](http://flask.pocoo.org/) or [Django](https://www.djangoproject.com/) would require maintaining state in a database.
API may differ in syntax and the application protocol may differ.

# Usage

### Start the server

    python pookeeper.py

### Start a telnet client to connect to the Twisted server.

    telnet [host] [port]

### Send commands

* Create node
    * `CREATE:[node_name]`
    * Example: `CREATE:/yolo`
    * Example: `CREATE:/yolo/baggins`
* Create ephemeral node
    * `ECREATE:[node_name]`
    * Example: `ECREATE:/yolo`
* Delete node
    * `DELETE:[node_name]`
    * Example: `DELETE:/yolo`
* Check if node exists
    * `EXISTS:[node_name]`
    * Example: `EXISTS:/yolo`
* Get data from a node
    * `GET:[node_name]`
    * Example: `GET:/yolo`
* Set data on a node
    * `SET:[node_name]`
    * Example: `SET:/yolo`
* Get name of all children of a node
    * `CHILDREN:[node_name]`
    * Example: `CHILDREN:/yolo` 
    * Note: children are in order which they were added.

# Currently Implemented Features

The goal of this project is to implement all features of ZooKeeper. It is not complete. The following is a list of ZooKeeper features currently implemented:

* Custom application-level protocol for TCP connections to talk with the server.
    * This is most likely NOT the same application-level protocol that the real ZooKeeper uses.
* Znodes API
    * create
    * delete
    * exists
    * get data
    * set data
    * get children
* Watchers
* Ephemeral Nodes
* Preserve order of children added. Maintained by parent.

# Feature not yet implemented

The following are a list of features to be implemented.

* __Replication__ a.k.a. ZooKeeper ensemble
* All guarantees associated with a ZooKeeper ensemble
* Znodes API
    * sync

# Unit-Tests

The unit tests are a tremendously important aspect of this project since they attempt to ensure the accuracy of the ZooKeeper implementation.

To run it from the project directory:

    python -m unittest test.test_pookeeper

# Contributing

Please add issues, pull requests, anything that you see fit. As stated above, this is an academic (as in 'for my personal understanding', not as in 'for a grade') so any feedback would be extremely helpful.

# "This is a very unfortunate name"

Another possible name for the project is [_Herpetologist_](https://en.wikipedia.org/wiki/Herpetology).
The logic behind is the following:

    type(Python) == 'reptile'
    ZooKeepers['reptile'] == 'herpetologist'
