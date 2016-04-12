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

IRONIC_IP = "127.0.0.1"
IRONIC_PORT = 69


class TFTPProxy(common.CommonService):

    def __init__(self):
        super(TFTPProxy, self).__init__('tftp_proxy')

    def request_handler(self, request):
        udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpsocket.bind(('', 0))

        udpsocket.sendto(request['data'], (IRONIC_IP, IRONIC_PORT))

        data, addr = udpsocket.recvfrom(32768)
        udpsocket.close()

        self.send_to_agent(
            request['agent_uuid'], request['request_uuid'], data)


def main():
    proxy = TFTPProxy()
    proxy.start()
