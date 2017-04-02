from pookeeper import ZooKeeperFactory
from twisted.trial import unittest
from twisted.test import proto_helpers


class PooKeeperTestCase(unittest.TestCase):

    def setUp(self):
        factory = ZooKeeperFactory()
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)


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
        

if __name__ == '__main__':
    unittest.main()
