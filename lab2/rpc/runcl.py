import rpc
import logging
import time

from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

def callback(data):
  print("ResultCallback: {}".format(data.value))


base_list = rpc.DBList({'foo'})
cl.append('bar', base_list, callback)

while cl.response is None:
  print("doing other things")
  time.sleep(1)


cl.stop()
