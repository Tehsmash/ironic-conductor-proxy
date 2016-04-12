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

IRONIC_IP = "127.0.0.1"
IRONIC_PORT = 69

# Socket to receive a packet from the agent
sockin = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
sockin.bind("tftp_insocket")

connected = False
while not connected:
    try:
        # Socket to send data back to the agent
        sockout = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        sockout.connect("outsocket")
    except Exception as e:
        print("Waiting for socket: %s" % e)
    else:
        connected = True


def response_handler(sock, ip):
    # Listen for response to UDP packet
    # Send response down the out socket
    data, addr = sock.recvfrom(32768)

    response = {
        'ip': ip,
        'data': data
    }

    sockout.sendall(json.dumps(response))


def request_handler():
    # Receive request from agent
    # Process request and send UDP packet
    while True:
        raw_request = sockin.recv(32768)
        request = json.loads(raw_request)

        udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpsocket.bind(('', 0))

        udpsocket.sendto(request['data'], (IRONIC_IP, IRONIC_PORT))

        thread.start_new_thread(response_handler, (udpsocket, request['ip']))

request_handler()
