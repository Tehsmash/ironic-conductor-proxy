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
import uuid
import base64

# Socket to receive data back from the service
sockin = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
sockin.bind("conductor_outsocket")

# Socket to send data to the service
sockout = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
sockout.connect("conductor_insocket")

# UPD Socket to listen to and send requests from
tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsocket.bind(('', 5123))
tcpsocket.listen(5)

requests = {}


def response_handler():
    # Receive response from service
    # Process and respond via updsocket
    while True:
        raw_response = sockin.recv(32768)
        response = json.loads(raw_response)

        print("New response!")

        conn = requests.get(response['uuid'])
        if conn:
            raw_data = base64.b64decode(response['data'])
            conn.send(raw_data)
            print("Response returned!")


def request_handler():

    while True:
        conn, addr = tcpsocket.accept()

        data = conn.recv(32768)

        print("New request!")

        connection_id = str(uuid.uuid4())
        encoded = base64.b64encode(data)

        request = {
            'uuid': connection_id,
            'data': encoded
        }

        requests[connection_id] = conn

        sockout.sendall(json.dumps(request))

        print("Sent request to proxy")

thread.start_new_thread(response_handler, tuple())
request_handler()

sockin.close()
