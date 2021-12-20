import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
print("Connecting to client...")

while True:
    #  Wait for next request from client
    message = socket.recv()
    print("Received message: ")
    print(str(message))

    #  Do some 'work'
    time.sleep(1)

    #  Send reply back to client
    socket.send_string("Acknowledge")
    print("Sending message: Acknowledge")
