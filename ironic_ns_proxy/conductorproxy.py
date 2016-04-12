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
import base64

IRONIC_IP = "104.130.159.134"
IRONIC_PORT = 80

# Socket to receive a packet from the agent
sockin = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
sockin.bind("conductor_insocket")

connected = False
while not connected:
    try:
        # Socket to send data back to the agent
        sockout = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        sockout.connect("conductor_outsocket")
    except Exception as e:
        print("Waiting for socket: %s" % e)
    else:
        connected = True


def processor(request):
    # Listen for response to UDP packet
    # Send response down the out socket
    tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsocket.connect((IRONIC_IP, IRONIC_PORT))

    raw_data = base64.b64decode(request['data'])
    tcpsocket.send(raw_data)

    print("Request forwarded")

    data, addr = tcpsocket.recvfrom(32768)

    print("Upstream response received")

    response = {
        'uuid': request['uuid'],
        'data': base64.b64encode(data)
    }

    sockout.sendall(json.dumps(response))

    print("Response forwarded to agent")


def request_handler():
    # Receive request from agent
    # Process request and send UDP packet
    while True:
        raw_request = sockin.recv(32768)
        request = json.loads(raw_request)

        print("New request!")

        thread.start_new_thread(processor, (request,))

request_handler()
