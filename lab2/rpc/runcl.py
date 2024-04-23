import rpc
import logging

from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

def callback(data):
  print("ResultCallback: {}".format(data.value))


base_list = rpc.DBList({'foo'})
result_list = cl.append('bar', base_list, callback)

print("Result: {}".format(result_list.value))

cl.stop()
