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

import socket

from ironic_ns_proxy import common


class ConductorAgent(common.CommonAgent):

    def __init__(self):
        super(ConductorAgent, self).__init__('conductor_proxy')
        self.tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.requests = {}

    def response_handler(self, response):
        conn = self.requests.pop(response['request_uuid'])
        if conn:
            conn.send(response['data'])
            conn.close()

    def request_handler(self):
        conn, addr = self.tcpsocket.accept()
        data = conn.recv(32768)

        print("New request!")

        request_id = self.send_to_proxy(data)
        self.requests[request_id] = conn

        print("Sent request to proxy")

    def clean_up(self):
        for request in self.requests.values():
            request.close()
        self.tcpsocket.close()

    def run(self):
        self.tcpsocket.bind(('', 5123))
        self.tcpsocket.listen(5)
        super(ConductorAgent, self).run()


def main():
    agent = ConductorAgent()
    agent.start()
