import sys

import zmq

import constPipe

me = str(sys.argv[1])

src = constPipe.SRC1 if me == '1' else constPipe.SRC2  # check task src host
prt = constPipe.PORT2 if me == '1' else constPipe.PORT3  # check task src port

address1 = "tcp://" + src + ":" + prt  # how and where to connect

context = zmq.Context()
reply_socket = context.socket(zmq.REP)  # create reply socket
 
reply_socket.bind(address1)  # bind socket to address

sumWords = {}

while True:
    message = reply_socket.recv()  # wait for incoming message
    if b"STOP" not in message:  # if not to stop...
        decoded_message = message.decode()
        if decoded_message in sumWords:
            sumWords[decoded_message] += 1
        else:
            sumWords[decoded_message] = 1
        print("{}: {}".format(decoded_message, sumWords[decoded_message]))
        reply_socket.send((message.decode() + "*").encode())  # append "*" to message
    else:  # else...
        break  # break out of loop and end
