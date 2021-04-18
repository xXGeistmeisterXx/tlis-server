# This is just a test script, should be gone by release

from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.protocols.basic import LineReceiver
import json
import time

class Tester(LineReceiver):
	def sendMessage(self, data):
		self.sendLine(data.encode("utf-8"))
		print("wrote data")

	def lineReceived(self, data):
		print(json.loads(data.decode("utf-8")))

	def connectionMade(self):
		print("connected")
		for obj in data:
			self.sendMessage(obj)

	def connectionLost(self, reason):
		print("disconnected")
		reactor.stop()

data = []
data.append(json.dumps({"id": 1, "customer_id": 1, "username":"me", "password":"changeMe123"}))
data.append(json.dumps({"type":"Customer", "action":"ADD", "number":"69", "first_name":"Tyler", "last_name":"Geist", "email":"name@email.com", "grade":9, "staff":0}))
data.append(json.dumps({"type":"Logout"}))

point = TCP4ClientEndpoint(reactor, "localhost", 6969)
d = connectProtocol(point, Tester())
reactor.run()
