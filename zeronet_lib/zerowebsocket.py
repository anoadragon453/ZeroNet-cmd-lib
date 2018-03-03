import websocket, sys
import json

class ZeroWebSocket(object):
	def __init__(self, wrapper_key, address="127.0.0.1:43110", secure=False):
		self.ws = websocket.create_connection("%s://%s/Websocket?wrapper_key=%s" % ("wss" if secure else "ws", address, wrapper_key))

		self.next_id = 1

	def __enter__(self):
		return self
	def __exit__(self, exc_type, exc_value, traceback):
		self.ws.close()

	def send(self, cmd, *args, **kwargs):
		data = None
		if len(args) == 0:
			data = dict(cmd=cmd, params=kwargs, id=self.next_id)
		elif len(kwargs) == 0:
			data = dict(cmd=cmd, params=args, id=self.next_id)
		else:
			raise TypeError("Only args/kwargs alone are allowed in call to ZeroWebSocket")

		self.ws.send(json.dumps(data))

		while True:
			response = json.loads(self.ws.recv())
			if response["cmd"] == "response" and response["to"] == self.next_id:
				self.next_id += 1
				return response["result"]
			elif response["cmd"] == "error":
				self.next_id += 1
				raise ZeroWebSocket.Error(response["params"])

	class Error(Exception):
		pass