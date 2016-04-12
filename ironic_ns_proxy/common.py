# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import base64
import json
import os
import socket
import thread
import uuid


class Common(object):

    def __init__(self, name):
        self.unixsocket_name = name
        self.unixsocket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    def run(self):
        pass

    def clean_up(self):
        pass

    def start(self):
        # Make sure the socket does not already exist
        try:
            os.unlink(self.unixsocket_name)
        except OSError:
            if os.path.exists(self.unixsocket_name):
                raise

        try:
            self.unixsocket.bind(self.unixsocket_name)
            self.run()
        finally:
            self.clean_up()
            self.unixsocket.close()


class CommonService(Common):

    def __init__(self, name):
        super(CommonService, self).__init__(name)
        self.agents = {}

    def get_agent(self, agent_uuid):
        unixsocket = self.agents.get(agent_uuid)
        if not unixsocket:
            agent = "conductor_%s" % agent_uuid
            try:
                unixsocket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
                unixsocket.connect(agent)
            except Exception as e:
                print("Unable to connect or setup socket: %s" % e)
                return
            else:
                print("Connected to new agent %s" % agent_uuid)
                self.agents[agent_uuid] = unixsocket
        return unixsocket

    def send_to_agent(self, agent_uuid, request_uuid, data):
        agent = self.get_agent(agent_uuid)
        response = {
            'request_uuid': request_uuid,
            'data': base64.b64encode(data)
        }
        agent.sendall(json.dumps(response))

    def request_handler(self, request):
        pass

    def clean_up(self):
        for agent in self.agents.values():
            agent.close()

    def run(self):
        while True:
            raw_request = self.unixsocket.recv(32768)
            request = json.loads(raw_request)
            request['data'] = base64.b64decode(request['data'])
            print("New request!")
            thread.start_new_thread(self.request_handler, (request,))


class CommonAgent(Common):

    def __init__(self, proxy_id):
        self.agent_uuid = str(uuid.uuid4())
        super(CommonAgent, self).__init__("conductor_%s" % self.agent_uuid)
        self.proxy_id = proxy_id

    def get_proxy(self):
        try:
            unixsocket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            unixsocket.connect(self.proxy_id)
        except Exception as e:
            print("Unable to connect or setup socket: %s" % e)
            return
        return unixsocket

    def send_to_proxy(self, data):
        request_uuid = str(uuid.uuid4())
        proxy = self.get_proxy()
        request = {
            'agent_uuid': self.agent_uuid,
            'request_uuid': request_uuid,
            'data': base64.b64encode(data)
        }
        proxy.sendall(json.dumps(request))
        return request_uuid

    def _response_handler(self):
        while True:
            raw_response = self.unixsocket.recv(32768)
            response = json.loads(raw_response)
            response['data'] = base64.b64decode(response['data'])
            thread.start_new_thread(self.response_handler, (response,))

    def response_handler(self, response):
        pass

    def request_handler(self):
        pass

    def run(self):
        thread.start_new_thread(self._response_handler, tuple())
        while True:
            self.request_handler()
