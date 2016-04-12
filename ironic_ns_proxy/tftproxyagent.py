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

import json
import socket
import thread

# Socket to receive data back from the service
sockin = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
sockin.bind("tftp_outsocket")

# Socket to send data to the service
sockout = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
sockout.connect("tftp_insocket")

# UPD Socket to listen to and send requests from
udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpsocket.bind(('', 69))


def response_handler():
    # Receive response from service
    # Process and respond via updsocket
    while True:
        raw_response = sockin.recv(32768)
        response = json.loads(raw_response)
        udpsocket.sendto(response['data'],
                         (response['ip'][0], response['ip'][1]))


def request_handler():

    while True:
        data, addr = udpsocket.recvfrom(32768)

        request = {
            'ip': addr,
            'data': data
        }

        sockout.sendall(json.dumps(request))


thread.start_new_thread(response_handler, tuple())
request_handler()

sockin.close()
