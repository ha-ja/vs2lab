import constRPC
import time
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
        self.server = None
        self.dataRecieved = False

    def run(self):
        self.chan.bind(self.client)
        self.server = self.chan.subgroup('server')

    def stop(self):
        self.chan.leave('client')

    def append(self, data, db_list):
        assert isinstance(db_list, DBList)
        msglst = (constRPC.APPEND, data, db_list)  # message payload
        self.chan.send_to(self.server, msglst)  # send msg to server
        while True:
            msgrcv = self.chan.receive_from(self.server)
            if msgrcv[1] == "ACK":
                print("Recieved Ack")
                break;

    def awaitResponse(self, callback):
        print("started waiting for response")
        while True:
            msgrcv = self.chan.receive_from(self.server)
            if msgrcv is not None:
                self.dataRecieved = True
                callback(msgrcv[1])
                break;

class Server:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.server = self.chan.join('server')
        self.timeout = 3

    @staticmethod
    def append(data, db_list):
        assert isinstance(db_list, DBList)  # - Make sure we have a list
        return db_list.append(data)

    def run(self):
        self.chan.bind(self.server)
        while True:
            msgreq = self.chan.receive_from_any(self.timeout)  # wait for any request
            if msgreq is not None:
                client = msgreq[0]  # see who is the caller
                msgrpc = msgreq[1]  # fetch call & parameters
                if constRPC.APPEND == msgrpc[0]:  # check what is being requested
                    print("Got request from client")
                    self.chan.send_to({client}, "ACK")
                    time.sleep(10)  
                    result = self.append(msgrpc[1], msgrpc[2])
                    self.chan.send_to({client}, result)  # return response
                else:
                    pass  # unsupported request, simply ignore