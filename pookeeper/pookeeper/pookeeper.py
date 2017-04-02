import os
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor


class ZooKeeper(LineReceiver):

    def __init__(self, znodes):
        self.znodes = znodes 


    def connectionMade(self):
        self.sendLine("Connected.")


    def createNode(self, node):
        # Check if znode path starts with a slash
        if node[0] != '/':
            self.handle_BADNODE(node)

        # Check path up to node exists
        p, _ = os.path.split(node)
        if p in self.znodes:
            self.handle_ADDNODE(node)
        else:
            self.handle_BADNODE(node)


    def lineReceived(self, msg):
        # Check command
        idx = msg.find(':')
        if idx == -1:
            self.handle_BADCOMMAND(msg)

        cmd = msg[:idx]
        if cmd == 'CREATE':        
            self.handle_CREATENODE(msg[(idx+1):])
        elif cmd == 'DELETE':
            self.handle_DELETENODE(msg[(idx+1):])
        elif cmd == 'EXISTS':
            self.handle_EXISTSNODE(msg[(idx+1):])
        elif cmd == 'GET':
            self.handle_GET(msg[(idx+1):])
        elif cmd == 'SET':
            self.handle_SET(msg[(idx+1):])
        elif cmd == 'CHILDREN':
            self.handle_GETCHILDREN(msg[(idx+1):])
        else:
            self.sendLine('false')


    def handle_CREATENODE(self, node):
        # Check if znode path starts with a slash
        if node[0] != '/':
            self.sendLine('false')

        # Check path up to node exists
        p, _ = os.path.split(node)
        if p not in self.znodes:
            self.sendLine('false')
        else:
            parent, child = os.path.split(node)
            self.znodes[node] = { 'parent': parent, 'children': {} }
            self.znodes[parent]['children'][child] = True
    
            self.sendLine('true')


    def handle_DELETENODE(self, node):
        # Check if znode path starts with a slash
        if node[0] != '/':
            self.sendLine('false')

        # Check that node exists
        if node in self.znodes:
            # Delete node from parent's children listing
            parent, child_name = os.path.split(node)
            del self.znodes[parent]['children'][child_name]

            # Delete node and all its children :(
            stack = [node]
            while len(stack):
                curr_node = stack.pop()
                stack.extend(self.znodes[curr_node]['children'].keys())
                del self.znodes[curr_node]
            self.sendLine('true')
        else:
            self.sendLine('false')

    def handle_EXISTSNODE(self, node):
        # Check if znode path starts with a slash
        if node[0] != '/':
            self.sendLine('false')

        # Check that node exists
        if node in self.znodes:
            self.sendLine('true')
        else:
            self.sendLine('false')

    def handle_GET(self, node):
        # Check if znode path starts with a slash
        if node[0] != '/':
            self.sendLine('false')

        # Check that node exists
        if node in self.znodes:
            self.sendLine(self.znodes[node]['data'])
        else:
            self.sendLine('false')

    def handle_SET(self, msg):
        idx = msg.find(':')
        if idx == -1:
            self.sendLine('false')

        node = msg[:idx]
        data = msg[(idx+1):]

        # Check if znode path starts with a slash
        if node[0] != '/':
            self.sendLine('false')

        # Check that node exists
        if node in self.znodes:
            self.znodes[node]['data'] = data
            self.sendLine('true')
        else:
            self.sendLine('false')

    def handle_GETCHILDREN(self, node):
        # Check if znode path starts with a slash
        if node[0] != '/':
            self.sendLine('false')

        # Check that node exists
        if node in self.znodes:
            self.sendLine(','.join(self.znodes[node]['children'].keys()))
        else:
            self.sendLine('false')
      
class ZooKeeperFactory(Factory):

    def __init__(self):
        self.znodes = {'/': { 'parent': None, 'children': {} } }


    def buildProtocol(self, addr):
        return ZooKeeper(self.znodes)


if __name__ == '__main__':
    reactor.listenTCP(8123, ZooKeeperFactory())
    print('Starting on port 8123')
    reactor.run()
