import argparse
import sys
import threading
import asyncio
import websockets
import logging

logging.basicConfig(level=logging.DEBUG)


__TOKEN_DB = []


def add_token(token, user, vmi_name):
    matches = [x for x in __TOKEN_DB if x["user"] == user and x["vmi"] == vmi_name]
    if len(matches) >= 1:
        return False
    __TOKEN_DB.append({"user": user, "vmi": vmi_name, "token": token})
    return True


def check_token(token, vmi_name):
    matches = [x for x in __TOKEN_DB if x["token"] == token]
    if len(matches) < 1:
        return False
    for match in matches:
        if match["vmi"] == vmi_name:
            return True
    return False


class WebsocketProxy:
    def __init__(self, remote_url, api_path):
        self.remote_url = remote_url
        self.api_path = api_path
        self.thread = None

    def run(self, host, port):
        start_server = websockets.serve(self.proxy, host, port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    def run_in_thread(self, host, port):
        start_server = websockets.serve(self.proxy, host, port)
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(start_server)
        self.thread = threading.Thread(target=self.loop.run_forever)
        self.thread.start()

    def stop_thread(self):
        if self.thread is not None:
            self.loop.call_soon_threadsafe(self.loop.stop)
            logging.info("Stopped loop")
            self.thread.join()
            logging.info("Stopped thread")

    async def proxy(self, websocket, path):
        '''Called whenever a new connection is made to the server'''
        # split path to get vmi name and token
        splitted = path.split("/")
        if len(splitted) != 3:
            logging.warning("Invalid URL")
            await websocket.close(reason="invalid url")
            return
        vmi_name = splitted[1]
        token = splitted[2]
        # check if user has permissions to access this vmi
        if not check_token(token, vmi_name):
            logging.warning("Invalid token")
            await websocket.close(reason="invalid token")
            return
        # build websocket url and connect to
        url = self.remote_url + self.api_path.format(vmi_name=vmi_name)
        async with websockets.connect(url) as ws:
            taskA = asyncio.create_task(WebsocketProxy.clientToServer(ws, websocket))
            taskB = asyncio.create_task(WebsocketProxy.serverToClient(ws, websocket))
            await taskA
            await taskB

    async def clientToServer(ws, websocket):
        async for message in ws:
            await websocket.send(message)

    async def serverToClient(ws, websocket):
        async for message in websocket:
            await ws.send(message)


def main():
    add_token("supersecret", "admin", "ubuntu-cloud-gnome")
    remote_url = "ws://localhost:8001"
    api_path = "/apis/subresources.kubevirt.io/v1alpha3/namespaces/default/virtualmachineinstances/{vmi_name}/vnc"
    wp = WebsocketProxy(remote_url, api_path)
    wp.run("localhost", 8765)


if __name__ == '__main__':
    main()
