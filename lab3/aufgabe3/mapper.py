import pickle
import sys
import time
import constPipe

import zmq
import string


me = str(sys.argv[1])


address1 = "tcp://" + constPipe.SRC1 + ":" + constPipe.PORT1  # 1st task src
address2 = "tcp://" + constPipe.SRC2 + ":" + constPipe.PORT2  # address for request socket
address3 = "tcp://" + constPipe.SRC2 + ":" + constPipe.PORT3  # address for request socket

context = zmq.Context()
pull_socket = context.socket(zmq.PULL)  # create a pull socket
pull_socket.connect(address1)  # connect to task source 1


requester1 = context.socket(zmq.REQ)  # create request socket
requester1.connect(address2) 


requester2 = context.socket(zmq.REQ)  # create request socket
requester2.connect(address3)

time.sleep(1) 

print("{} started".format(me))


while True:
    work = pickle.loads(pull_socket.recv())  # receive work from a source

    translator = str.maketrans('', '', string.punctuation)
    cleaned_sentence = work[1].translate(translator)
    print("Sent {}. request".format(cleaned_sentence))  # print ack
    for index, word in enumerate(cleaned_sentence.split()):
      if index % 2 == 0:
        requester1.send_string(word)  # send message and go on
        #print("Sent {}. request".format(word))  # print ack
        message = requester1.recv()  # block until response
        #print(message.decode())  # print result
      else: 
        requester2.send_string(word)  # send message and go on
        #print("Sent {}. request".format(word))  # print ack
        message = requester2.recv()  # block until response
        #print(message.decode())  # print result
      
