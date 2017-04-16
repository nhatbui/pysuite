from pookeeper import ZooKeeperFactory
from twisted.trial import unittest
from twisted.test import proto_helpers


class PooKeeperTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = ZooKeeperFactory()
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)
        self.assertTrue(self.tr.value(), 'true:Connected\r\n')


    def addNode(self, node):
        self.proto.lineReceived('CREATE:' + node)


    def deleteNode(self, node):
        self.proto.lineReceived('DELETE:' + node)


    def test_addNode(self):
        self.addNode('/nhat')
        self.assertTrue('/nhat' in self.proto.znodes)
        self.assertTrue('/' in self.proto.znodes)
        self.assertTrue(len(self.proto.znodes['/']['children']) == 1)
        self.assertTrue('nhat' in self.proto.znodes['/']['children'])
        self.assertTrue(self.proto.znodes['/nhat']['parent'] == '/')


    def test_deleteNode(self):
        self.addNode('/nhat')
        self.deleteNode('/nhat')
        self.assertTrue('/nhat' not in self.proto.znodes)
        self.assertTrue('/' in self.proto.znodes)
        self.assertTrue(len(self.proto.znodes['/']['children']) == 0)
       

    def test_exists(self):
        self.addNode('/nhat')
        # Flush responses
        self.tr.clear()
        self.proto.lineReceived('EXISTS:/nhat')
        self.assertEqual(self.tr.value(), 'true\r\n')
        # Flush responses
        self.tr.clear()
        self.proto.lineReceived('EXISTS:/bob')
        self.assertEqual(self.tr.value(), 'false\r\n')


    def test_setData(self):
        self.addNode('/nhat')
        self.proto.lineReceived('SET:/nhat:yolo baggins')
        self.assertEqual(self.proto.znodes['/nhat']['data'], 'yolo baggins')


    def test_getData(self):
        self.addNode('/nhat')
        self.proto.lineReceived('SET:/nhat:yolo baggins')
        # Flush responses
        self.tr.clear()
        self.proto.lineReceived('GET:/nhat')
        self.assertEqual(self.tr.value(), 'yolo baggins\r\n')


    def test_getChildren(self):
        self.addNode('/nhat')
        # Flush responses
        self.tr.clear()
        self.proto.lineReceived('CHILDREN:/')
        self.assertEqual(self.tr.value(), 'nhat\r\n')


    def test_watch(self):
        self.addNode('/nhat')

        # Make new client who cares about this node
        new_proto = self.factory.buildProtocol(('127.0.0.1', 1))
        new_tr = proto_helpers.StringTransport()
        new_proto.makeConnection(new_tr)

        # New client watches node
        new_proto.lineReceived('WATCH:/nhat')

        # Delete this node
        self.deleteNode('/nhat')

        # Check if client got a notice
        # NOTE: during our checks there's no '\n' char because split()
        # removed it.
        client_msgs = new_tr.value().split('\n')
        self.assertEqual(client_msgs[1], 'true:WATCHING:/nhat\r')
        self.assertEqual(client_msgs[2], 'true:WATCHER_NOTICE:DELETED:/nhat\r')

        #print('new_tr')
        #print(new_tr.value())
        #print('self.tr')
        #print(self.tr.value())


    def test_ephemeral(self):
        self.proto.lineReceived('ECREATE:/nhat')

        # Check node added like a normal node
        self.assertTrue('/nhat' in self.proto.znodes)
        self.assertTrue('/' in self.proto.znodes)
        self.assertTrue(len(self.proto.znodes['/']['children']) == 1)
        self.assertTrue('nhat' in self.proto.znodes['/']['children'])
        self.assertTrue(self.proto.znodes['/nhat']['parent'] == '/')

        # Check if client got messages as expected
        orig_client_msgs = self.tr.value().split('\n')
        self.assertEqual(orig_client_msgs[0], 'true:Connected\r')
        self.assertEqual(orig_client_msgs[1], 'true:CREATED_ENODE:/nhat\r')
        
        # Make new client who cares about this node
        new_proto = self.factory.buildProtocol(('127.0.0.1', 1))
        new_tr = proto_helpers.StringTransport()
        new_proto.makeConnection(new_tr)

        # New client watches node
        new_proto.lineReceived('WATCH:/nhat')

        # Check that a watcher obj has been added to list
        self.assertTrue(len(self.proto.znodes['/nhat']['watchers']) == 1)

        # Disconnect connection
        #del self.proto
        self.proto.connectionLost()

        # Check if client got a notice
        # NOTE: during our checks there's no '\n' char because split()
        # removed it.
        client_msgs = new_tr.value().split('\n')
        self.assertEqual(client_msgs[1], 'true:WATCHING:/nhat\r')
        self.assertEqual(client_msgs[2], 'true:WATCHER_NOTICE:DELETED:/nhat\r')


    def test_addAlreadyExist(self):
        self.addNode('/nhat')
        self.assertTrue('/nhat' in self.proto.znodes)
        self.assertTrue('/' in self.proto.znodes)
        self.assertTrue(len(self.proto.znodes['/']['children']) == 1)
        self.assertTrue('nhat' in self.proto.znodes['/']['children'])
        self.assertTrue(self.proto.znodes['/nhat']['parent'] == '/')
        self.tr.clear()
        self.addNode('/nhat')

        self.assertEqual(self.tr.value().split(':')[0], 'false')
        self.assertTrue('/nhat' in self.proto.znodes)
        self.assertTrue('/' in self.proto.znodes)
        self.assertTrue(len(self.proto.znodes['/']['children']) == 1)
        self.assertTrue('nhat' in self.proto.znodes['/']['children'])
        self.assertTrue(self.proto.znodes['/nhat']['parent'] == '/')


    def test_leaderElection(self):
        self.addNode('/leader')

        # Check node added like a normal node
        self.assertTrue('/leader' in self.proto.znodes)
        self.assertTrue('/' in self.proto.znodes)
        self.assertTrue(len(self.proto.znodes['/']['children']) == 1)
        self.assertTrue('leader' in self.proto.znodes['/']['children'])
        self.assertTrue(self.proto.znodes['/leader']['parent'] == '/')

        def add_candidate(candidate, transportProtocol):
            transportProtocol.clear()
    
            candidate.lineReceived('ECREATE:/leader/{}:{}'.format(*candidate.address))

            # Check node added like a normal node
            self.assertTrue('/leader/{}:{}'.format(*candidate.address) in self.proto.znodes)
            self.assertTrue('{}:{}'.format(*candidate.address) in self.proto.znodes['/leader']['children'])
            self.assertTrue(self.proto.znodes['/leader/{}:{}'.format(*candidate.address)]['parent'] == '/leader')

            transportProtocol.clear()
    
            # check which children exists
            candidate.lineReceived('CHILDREN:/leader')
            children_str = transportProtocol.value().strip()

            if len(self.proto.znodes['/leader']['children']) == 0:
                self.assertEqual(children_str, '')

            children = children_str.split(',')
            if children[0] == '{}:{}'.format(*candidate.address):
                print('{} is leader'.format(candidate.address))
            else:
                i = children.index('{}:{}'.format(*candidate.address))
                num_watchers = len(self.proto.znodes['/leader/{}'.format(children[i-1])]['watchers'])
                candidate.lineReceived('WATCH:/leader/{}'.format(children[i-1]))
                # Check that a watcher obj has been added to list
                self.assertEqual(len(self.proto.znodes['/leader/{}'.format(children[i-1])]['watchers']), num_watchers + 1)

            transportProtocol.clear()

        # Make new client who adds itself to leader node
        new_proto = self.factory.buildProtocol(('127.0.0.1', 1))
        new_tr = proto_helpers.StringTransport()
        new_proto.makeConnection(new_tr)

        add_candidate(self.proto, self.tr)
        add_candidate(new_proto, new_tr)

        self.proto.connectionLost()

        self.assertEqual(new_tr.value().strip(), 'true:WATCHER_NOTICE:DELETED:/leader/127.0.0.1:0')


if __name__ == '__main__':
    unittest.main()
