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
import sys

from ironic_ns_proxy import common


class ConductorProxy(common.CommonService):
    def __init__(self, ironic_ip, ironic_port):
        self.ironic_ip = ironic_ip
        self.ironic_port = ironic_port
        super(ConductorProxy, self).__init__('conductor_proxy')

    def request_handler(self, request):
        # Listen for response to UDP packet
        # Send response down the out socket
        tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpsocket.connect((self.ironic_ip, self.ironic_port))
        tcpsocket.send(request['data'])

        print("Request forwarded")

        data, addr = tcpsocket.recvfrom(32768)
        tcpsocket.close()

        print("Upstream response received")

        self.send_to_agent(
            request['agent_uuid'], request['request_uuid'], data)

        print("Response forwarded to agent")


def main(args=sys.argv):
    proxy = ConductorProxy(*args[1:])
    proxy.start()
