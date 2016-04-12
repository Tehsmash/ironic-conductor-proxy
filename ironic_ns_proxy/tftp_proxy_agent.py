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


class TFTPAgent(common.CommonAgent):

    def __init__(self):
        super(TFTPAgent, self).__init__('tftp_proxy')
        self.udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.requests = {}

    def response_handler(self, response):
        addr = self.requests[response['request_uuid']]
        self.udpsocket.sendto(response['data'], addr)

    def request_handler(self):
        data, addr = self.udpsocket.recvfrom(32768)
        request_id = self.send_to_proxy(data)
        self.requests[request_id] = addr

    def clean_up(self):
        self.udpsocket.close()

    def run(self):
        self.udpsocket.bind(('', 69))
        super(TFTPAgent, self).run()


def main():
    agent = TFTPAgent()
    agent.start()
