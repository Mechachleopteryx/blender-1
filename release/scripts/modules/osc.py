# osc

# pip3 install python-osc
from pythonosc import dispatcher
from pythonosc import osc_server

import threading
import asyncio
import socket
import math

def deg2rad(deg):
    return math.radians(deg)

class Server:
    def __init__(self, module):
        if "bpy" == module:
            import bpy
            self.module = bpy
        else:
            self.module = None
        self.loop = asyncio.get_event_loop()

    def serve(self, server, ip, port):
        factory = server._OSCProtocolFactory(server.dispatcher)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass
        sock.settimeout(0.0)
        sock.bind((ip, port))
        listen = server._loop.create_datagram_endpoint(lambda: factory, sock=sock)
        server._loop.run_until_complete(listen)

    def handle_knob(self, tag, arg, val):
        print("handle_knob %s 0x%02x 0x%02x" % (tag, arg, val))
        if self.module is not None:
            bpy = self.module
            o = bpy.context.scene.objects.active
            deg = 10 if 1 == val else -10
            if   arg == 71: # 0x41
                o.rotation_euler[0] += deg2rad(deg)
            elif arg == 72: # 0x42
                o.rotation_euler[1] += deg2rad(deg)
            elif arg == 73: # 0x43
                o.rotation_euler[2] += deg2rad(deg)

    def start(self, port):
        ip = "127.0.0.1"
        dispat = dispatcher.Dispatcher()
        dispat.map("/knob", self.handle_knob)
        self.server = osc_server.AsyncIOOSCUDPServer((ip, port), dispat, self.loop)
        self.serve(self.server, ip, port)
        threading.Thread(target=self.loop.run_forever).start()

    def stop(self):
        print("closing...")
        self.loop.call_soon_threadsafe(self.loop.stop)

if __name__ == '__main__':
    PORT = 5005
    serv = Server(None)
    serv.start(PORT)
    serv.stop()
    serv.start(PORT)
    print("serv", PORT, "...")
    input(">> ")
    serv.stop()
