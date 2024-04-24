import rpc
import logging
import threading
import time

from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

def callback(data):
  print("ResultCallback: {}".format(data.value))

waitthread = threading.Thread(target=cl.awaitResponse, args=(callback,))

base_list = rpc.DBList({'foo'})
cl.append('bar', base_list)
waitthread.start()


while cl.dataRecieved == False:
  print("Do other things.")
  time.sleep(1)


waitthread.join()

cl.stop()
