import zmq
import serial

ser = serial.Serial(
    port='/dev/rfcomm0',
    baudrate=9600,
)

context = zmq.Context()

#  Socket to talk to server
print("Connecting to server...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
print("Client connected to the server.")

while 1:
    b1 = ser.read()
    # print(b1)
    if b1 == b'M':
        b2 = ser.read()
        if b2 == b'V':
            b3 = ser.read()
            if b3 == b'R':
                b4 = ser.read()
                if b4 == b'T':
                    print("Sending message:")
                    socket.send_string("MVRT")
                    print("MVRT")
                    #  Get the reply.
                    message = socket.recv()
                    print("Received reply: " + str(message))
            elif b3 == b'L':
                b4 = ser.read()
                if b4 == b'F':
                    print("Sending message:")
                    socket.send_string("MVLF")
                    print("MVLF")
                    #  Get the reply.
                    message = socket.recv()
                    print("Received reply: " + str(message))
            elif b3 == b'U':
                b4 = ser.read()
                if b4 == b'P':
                    print("Sending message:")
                    socket.send_string("MVUP")
                    print("MVUP")
                    #  Get the reply.
                    message = socket.recv()
                    print("Received reply: " + str(message))
            elif b3 == b'D':
                b4 = ser.read()
                if b4 == b'N':
                    print("Sending message:")
                    socket.send_string("MVDN")
                    print("MVDN")
                    #  Get the reply.
                    message = socket.recv()
                    print("Received reply: " + str(message))
    elif b1 == b'F':
        b2 = ser.read()
        if b2 == b'F':
            b3 = ser.read()
            if b3 == b'W':
                b4 = ser.read()
                if b4 == b'D':
                    print("Sending message:")
                    socket.send_string("FFWD")
                    print("FFWD")
                    message = socket.recv()
                    print("Received reply: " + str(message))
    elif b1 == b'P':
        b2 = ser.read()
        if b2 == b'L':
            b3 = ser.read()
            if b3 == b'A':
                b4 = ser.read()
                if b4 == b'Y':
                    print("Sending message:")
                    socket.send_string("PLAY")
                    print("PLAY")
                    message = socket.recv()
                    print("Received reply: " + str(message))
    elif b1 == b'R':
        b2 = ser.read()
        if b2 == b'W':
            b3 = ser.read()
            if b3 == b'N':
                b4 = ser.read()
                if b4 == b'D':
                    print("Sending message:")
                    socket.send_string("RWND")
                    print("RWND")
                    message = socket.recv()
                    print("Received reply: " + str(message))
    elif b1 == b'Z':
        b2 = ser.read()
        if b2 == b'M':
            b3 = ser.read()
            if b3 == b'I':
                b4 = ser.read()
                if b4 == b'N':
                    print("Sending message:")
                    socket.send_string("ZMIN")
                    print("ZMIN")
                    message = socket.recv()
                    print("Received reply: " + str(message))
            elif b3 == b'O':
                b4 = ser.read()
                if b4 == b'T':
                    print("Sending message:")
                    socket.send_string("ZMOT")
                    print("ZMOT")
                    message = socket.recv()
                    print("Received reply: " + str(message))
                