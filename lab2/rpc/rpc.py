import constRPC
import time
import threading

from context import lab_channel


class DBList:
    def __init__(self, basic_list):
        self.value = list(basic_list)

    def append(self, data):
        self.value = self.value + [data]
        return self


class Client:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.client = self.chan.join('client')
        self.channel = lab_channel.Channel()
        self.clientMiddleware = self.channel.join('clientmiddleware')
        self.server = None
        self.middleware = None

    def run(self):
        self.chan.bind(self.client)
        self.server = self.chan.subgroup('server')
        self.channel.bind(self.clientMiddleware)
        self.middleware = self.channel.subgroup('middleware')

    def stop(self):
        self.chan.leave('client')
        self.channel.leave('middleware')

    @staticmethod
    def recieve_ack(self, data, db_list):
        assert isinstance(db_list, DBList)
        msglst = (constRPC.APPEND, data, db_list)  # message payload
        # Funktion, die im Thread ausgeführt wird
        def thread_function():
            self.chan.send_to(self.server, msglst)  # send msg to server

        # Erstellen und Starten des Threads
        thread1 = threading.Thread(target=thread_function)

        self.channel.send_to(self.middleware, msglst) # send msg to middleware
        ack = self.channel.receive_from(self.middleware)  # wait for response
        print("ACK: ", ack)
        thread1.start()
        
        # Warten, bis der Thread beendet ist
        thread1.join()
        
            
    
    def append(self, data, db_list):
        self.recieve_ack(self, data, db_list)
        msgrcv = self.chan.receive_from(self.server)  # wait for response
        return msgrcv[1]  # pass it to caller


class Server:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.server = self.chan.join('server')
        self.channel = lab_channel.Channel()
        self.middleware = self.channel.join('middleware')
        self.timeout = 3

    @staticmethod
    def append(data, db_list):
        assert isinstance(db_list, DBList)  # - Make sure we have a list
        return db_list.append(data)

    def run(self):
        self.chan.bind(self.server)
        self.channel.bind(self.middleware)
        while True:
            msgreqmiddleware = self.channel.receive_from_any(self.timeout)  # wait for any request
            if msgreqmiddleware is not None:
                client = msgreqmiddleware[0]  # see who is the caller
                self.channel.send_to({client}, '200 OK')

            msgreq = self.chan.receive_from_any(self.timeout)  # wait for any request
            if msgreq is not None:
                client = msgreq[0]  # see who is the caller
                self.channel.send_to({client}, '200 OK')
                msgrpc = msgreq[1]  # fetch call & parameters
                time.sleep(7)
                if constRPC.APPEND == msgrpc[0]:  # check what is being requested
                    result = self.append(msgrpc[1], msgrpc[2])  # do local call
                    self.chan.send_to({client}, result)  # return response
                else:
                    pass  # unsupported request, simply ignore