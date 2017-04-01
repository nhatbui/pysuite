import os
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor


class ZooKeeper(LineReceiver):

    def __init__(self, znodes):
        self.znodes = znodes 


    def connectionMade(self):
        self.sendLine("Connected.")


    def lineReceived(self, node):
        # Check if znode path starts with a slash
        if node[0] != '/':
            self.handle_BADNODE(node)

        # Check path up to node exists
        p, _ = os.path.split(node)
        if p in self.znodes:
            self.handle_ADDNODE(node)
        else:
            self.handle_BADNODE(node)


    def handle_BADNODE(self, node):
        self.sendLine("Bad node.")


    def handle_ADDNODE(self, node):
        parent, child = os.path.split(node)
        self.znodes[node] = { 'parent': parent, 'children': [] }
        self.znodes[parent]['children'].append(child)

        self.sendLine("Node successfully added.")


class ZooKeeperFactory(Factory):

    def __init__(self):
        self.znodes = {'/': { 'parent': None, 'children': [] } }


    def buildProtocol(self, addr):
        return ZooKeeper(self.znodes)


reactor.listenTCP(8123, ZooKeeperFactory())
print('Starting on port 8123')
reactor.run()
