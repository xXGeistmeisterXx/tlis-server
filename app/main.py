# Welcome to the TLIS server code!
# TLIS stands for The Lasangna Inventory System
# It is a replacement of TSIS (The Spaghetti Inventory System)
# The program to add records to the db is tlis_server
# The service in systemd is also tlis_server
# Finally the debian package is also tlis_server
# This code was written by Tyler Geist
# Good luck and try not to break anything
# (also this needs to be run as root)

from twisted.internet.protocol import Factory, Protocol
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
import json
import manager
import time
import os

IP = "0.0.0.0"
PORT = 6969

print("something")

# get password from password file
manager.PASSWORD = os.getenv('DB_PASSWORD')

# Protocol for connections outgoing and ingoing
class TLIP(LineReceiver):

	def __init__(self, users):
		self.users = users
		self.username = None
		self.state = "AUTH"

	def connectionMade(self):
		print("connection made")

	def connectionLost(self, reason):
		print("connection lost")
		if self.username in self.users:
			del self.users[self.username]

	def lineReceived(self, data):
		print(data.decode("utf-8"))
		data = json.loads(data.decode("utf-8"))
		print(data)
		if self.state == "AUTH":
			self.handle_AUTH(data)
		else:
			self.handle_REQUEST(data)

	def handle_AUTH(self, data):
		print("AUTH")
		if not manager.auth(data):
			self.transport.abortConnection()
		else:
			if data["username"] in self.users:
				del self.users[self.username]
			self.username = data["username"]
			self.users[data["username"]] = self
			self.state = "CONNECTED"
			for obj in manager.login():
				print(obj)
				self.sendLine(json.dumps(obj).encode("utf-8"))

	def handle_REQUEST(self, data):
		print("REQUEST")
		if data["type"] == "Logout" or data["type"] == "Tech":
			self.transport.abortConnection()
		if data["type"] in manager.types:
			try:
				data = manager.run(data)
			except Exception as e:
				data = {"type":"Error", "error_type":str(type(e).__name__), "reason":str(e)}
			if data["type"] == "Error":
				self.sendLine(json.dumps(data).encode("utf-8"))
				return
			for protocol in self.users.values():
				protocol.sendLine(json.dumps(data).encode("utf-8"))

# inits new instances of TLIP Protocols
class TLIPFactory(Factory):

	def __init__(self):
		self.users = {}

	def buildProtocol(self, addr):
		return TLIP(self.users)

reactor.listenTCP(PORT, TLIPFactory(), interface=IP)
reactor.run()
print("running")
