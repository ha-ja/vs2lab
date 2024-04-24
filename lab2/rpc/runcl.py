import rpc
import logging
import threading

from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

# Funktion, die im Thread ausgeführt wird
def thread_function(name, callback):
    base_list = rpc.DBList({'foo'})
    result_list = cl.append('bar', base_list)
    callback(result_list)

# Callback-Funktion, die aufgerufen wird, wenn der Thread beendet ist
def callback_function(result_list):
    print("Result: {}".format(result_list.value))

# Erstellen und Starten des Threads
thread1 = threading.Thread(target=thread_function, args=("Thread 1", callback_function))
thread1.start()

print("Wo bin ich?")
print("Was bin ich?")
print("HAALLLOOOOO?")


# Warten, bis der Thread beendet ist
thread1.join()


cl.stop()
