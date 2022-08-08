import threading
import socket
import pickle


class SGW(threading.Thread):

    def __init__(self, n1, n2):

        threading.Thread.__init__(self)

        self.enodbs = []

        self.enbs = list(range(n1))

        self.n1 = n1

        self.ebu = [-5] * n2  # enod har user

        self.ii = []  # session be enod

        self.jj = []  # ack session be enod

        self.data_for_send = []  # ferestadan data

        self.gbuff = []  # gather buffer

        self.users = list(range(n2))

        self.bfs = []  # bufferi ke omade ro befrestam jayi ke bayad

        self.hfs = []  # handover ke omade ro befrestam jayi ke bayad
        self.enb_p = [i + 8000 for i in self.enbs]

    def l_mme(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 9090))
        sock.listen(10)

        while True:

            connection, client_address = sock.accept()

            while True:

                data1 = connection.recv(1024)

                if data1:

                    kc = pickle.loads(data1)
                    print(f'SGW from MME receiving:      **{kc}**')

                    if kc['type'] == 'Change route':
                        self.ebu[kc['value'][1]] = kc['value'][0]

                if not data1:
                    break

        return

    def l_enodb(self, i):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 8500 + i))
        sock.listen(10)

        while True:

            connection, client_address = sock.accept()

            while True:

                data1 = connection.recv(1024)

                if data1:

                    kc = pickle.loads(data1)
                    print(f'SGW from eNodeB receiving:      **{kc}**')
                    if kc['type'] == "eNodeB-SGW connection":
                        self.enodbs.append(kc['value'])

                    if kc['type'] == 'Create Session':
                        self.ii.append((kc['value'][0], kc['value'][1]))

                    if kc['type'] == 'Create Session Ack':
                        self.jj.append((kc['value'][0], kc['value'][1]))

                    if kc['type'] == 'Data Carrier':
                        self.data_for_send.append(kc['value'])

                    if kc['type'] == 'Send Me Buffered data':
                        self.gbuff.append(kc['value'])

                    if kc['type'] == 'Buffered data':
                        self.bfs.append(kc['value'])

                    if kc['type'] == 'Handover complete':
                        self.hfs.append(kc['value'])

                if not data1:
                    break

        return

    def send(self):

        while True:

            if self.bfs:
                data = {}
                data['type'] = "Buffered data"
                data['value'] = self.bfs[0]
                self.bfs.pop(0)
                x = pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', self.enb_p[data['value'][1]]))
                s.sendall(x)
                s.close()

            if self.hfs:
                data = {}
                data['type'] = "Handover complete"
                data['value'] = self.hfs[0]
                self.hfs.pop(0)
                x = pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', self.enb_p[data['value']]))
                s.sendall(x)
                s.close()

            if self.gbuff:
                data = {}

                data['type'] = "Send Me Buffered data"
                data['value'] = self.gbuff[0]
                self.gbuff.pop(0)
                x = pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', self.enb_p[data['value'][1]]))
                s.sendall(x)
                s.close()

            if self.ii:
                print(self.ii)
                h = self.ebu[self.ii[0][1]]
                data = {}
                data['type'] = "Create Session"
                data['value'] = self.ii[0]
                self.ii.pop(0)
                x = pickle.dumps(data)

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', self.enb_p[h]))
                s.sendall(x)
                s.close()

            if self.jj:
                h = self.ebu[self.jj[0][0]]
                data = {}

                data['type'] = "Create Session Ack"
                data['value'] = self.jj[0]
                self.jj.pop(0)
                x = pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', self.enb_p[h]))
                s.sendall(x)
                s.close()

            if self.data_for_send:
                data = {}

                data['type'] = "Data Carrier"
                data['value'] = self.data_for_send[0]
                a = self.data_for_send[0]
                self.data_for_send.pop(0)
                x = pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', self.enb_p[self.ebu[a[1]]]))
                s.sendall(x)
                s.close()

        return

    def run1(self):

        t = []

        for j in range(self.n1):
            t1 = threading.Thread(target=self.l_enodb, args=(j,))

            t1.start()
            t.append(t1)

        t3 = threading.Thread(target=self.l_mme)
        t2 = threading.Thread(target=self.send)

        t2.start()
        t3.start()

        t.append(t3)
        t.append(t2)

        for n in t:
            n.join()
