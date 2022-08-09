import threading
import socket
import pickle
import math as m


class eNodeB(threading.Thread):

    def __init__(self, id, location, n):  # takes in id, location and number of nodes
        threading.Thread.__init__(self)
        self.id = id
        self.loc = location
        self.end = 0

        self.pan = []  # position announcements from users
        self.uloc = []  # location of users for mme
        self.ss_to_send = []  # session to sgw
        self.ss_to_ack = []  # ack to sgw
        self.ack_to_r = []  # session to reciever
        self.ack_to_s = []  # ack session to sender

        self.users = list(range(n))
        self.ebuff = []  # ask to send bufferd data
        self.ur = [0] * n  # if user[i] is registered with us or not
        self.data_for_send = []  # doutgoing data
        self.buffd = []  # buffered data from sgw
        self.gbuffy = []  # buffered data for new enode
        self.inpos = [0] * n  # user in enodeb distance?
        self.po = []

        self.p_sgw = 8500 + self.id
        self.p_mme = 7500 + self.id

        self.enod_sgw_c = 1
        self.enod_mme_c = 1

    def l_sgw(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 8000 + self.id))
        sock.listen(10)

        while True:
            connection, client_address = sock.accept()
            while True:
                data1 = connection.recv(1024)
                if data1:
                    kc = pickle.loads(data1)
                    print(f'eNodeB{self.id} from SGW receiving:      **{kc}**')
                    if kc['type'] == 'Create Session':
                        self.ack_to_r.append((kc['value'][0], kc['value'][1]))

                    if kc['type'] == 'Create Session Ack':
                        self.ack_to_s.append((kc['value'][0], kc['value'][1]))

                    if kc['type'] == 'Data Carrier':
                        self.buffd.append(kc['value'])

                    if kc['type'] == 'Send Me Buffered data':
                        kk = [(item, kc['value'][2]) for item in self.buffd if item[1] == kc['value'][1]]
                        if kk:
                            for i in range(len(kk)):
                                self.gbuffy.append(kk[i])

                    if kc['type'] == 'Buffered data':
                        self.buffd.append(kc['value'][0])

                    if kc['type'] == 'Handover complete':
                        self.po.append(kc['value'])


                if not data1:
                    break

    def l_mme(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 7000 + self.id))
        sock.listen(10)

        while True:
            connection, client_address = sock.accept()
            while True:
                data1 = connection.recv(1024)
                if data1:
                    kc = pickle.loads(data1)
                    print(f'eNodeB{self.id} from MME receiving:      **{kc}**')
                    if kc['type'] == 'User Registration1':
                        self.ur[kc['value'][0]] = 1
                        self.inpos[kc['value'][0]] = 1
                        if kc['value'][1] != -10:
                            self.ebuff.append((kc['value'][1], kc['value'][0]))

                    if kc['type'] == 'User deregistration':
                        self.inpos[kc['value']] = 0

                if not data1:
                    break


    def l_data(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 6000 + self.id))
        sock.listen(10)

        while True:
            connection, client_address = sock.accept()
            while True:
                data1 = connection.recv(1024)

                if data1:
                    kc = pickle.loads(data1)
                    print(f'eNodeB{self.id} from data_path receiving:      **{kc}**')
                    if kc['type'] == 'Create Session':
                        self.ss_to_send.append((kc['value'][0], kc['value'][1]))

                    if kc['type'] == 'Create Session Ack':
                        self.ss_to_ack.append((kc['value'][0], kc['value'][1]))

                    if kc['type'] == 'Data Carrier':
                        self.data_for_send.append(kc['value'])

                if not data1:
                    break


    def l_sig(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 5000 + self.id))
        sock.listen(10)

        while True:
            connection, client_address = sock.accept()
            while True:
                data1 = connection.recv(1024)
                if data1:
                    kc = pickle.loads(data1)
                    print(f'eNodeB{self.id} from signal_path receiving:      **{kc}**')
                    if kc['type'] == 'Position announcement':
                        self.pan.append(kc['value'])

                    if kc['type'] == 'My Location':
                        d = m.sqrt((self.loc[0] - kc['value'][1][0]) ** 2 + ((self.loc[1] - kc['value'][1][1]) ** 2))
                        self.uloc.append((self.id, kc['value'][0], d))

                if not data1:
                    break

    def send(self):

        while True:
            # print(f"eNodeB {self.id} send mode...")

            if self.enod_sgw_c == 1:
                self.enod_sgw_c = 0
                data = {}
                data['type'] = "eNodeB-SGW connection"
                data['value'] = self.id
                x = pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', self.p_sgw))
                s.sendall(x)
                s.close()

            if self.enod_mme_c == 1:
                self.enod_mme_c = 0
                data = {}
                data['type'] = "eNodeB-MME connection"
                data['value'] = self.id
                x = pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', self.p_mme))
                s.sendall(x)
                s.close()

            if self.uloc:
                data = {}
                data['type'] = 'User distance'
                data['value'] = self.uloc[0]
                self.uloc.pop(0)
                x = pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', self.p_mme))
                s.sendall(x)
                s.close()

            if 1 in self.ur:
                a = self.ur.index(1)
                self.ur[a] = 0
                data = {}
                data['type'] = 'User Registration2'
                data['value'] = self.id
                x = pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', 3000 + a))
                s.sendall(x)
                s.close()

            if self.ss_to_send:
                data = {}
                data['type'] = 'Create Session'
                data['value'] = self.ss_to_send[0]
                self.ss_to_send.pop(0)
                x = pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', 8500 + self.id))
                s.sendall(x)
                s.close()

            if self.ack_to_r:
                data = {}
                data['type'] = 'Create Session'
                data['value'] = self.ack_to_r[0]
                self.ack_to_r.pop(0)
                x = pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', 4000 + data['value'][1]))
                s.sendall(x)
                s.close()

            if self.ss_to_ack:
                data = {}
                data['type'] = 'Create Session Ack'
                data['value'] = self.ss_to_ack[0]
                self.ss_to_ack.pop(0)
                x = pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', 8500 + self.id))
                s.sendall(x)
                s.close()

            if self.ack_to_s:
                data = {}
                data['type'] = 'Create Session Ack'
                data['value'] = self.ack_to_s[0]
                self.ack_to_s.pop(0)
                x = pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', 4000 + data['value'][0]))
                s.sendall(x)
                s.close()

            if self.data_for_send:
                data = {}
                data['type'] = 'Data Carrier'
                data['value'] = self.data_for_send[0]
                self.data_for_send.pop(0)
                x = pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', 8500 + self.id))
                s.sendall(x)
                s.close()

            if self.ebuff:
                data = {}
                data['type'] = 'Send Me Buffered data'
                a = self.ebuff[0]
                data['value'] = (a[0], a[1], self.id)
                self.ebuff.pop(0)
                x = pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', 8500 + self.id))
                s.sendall(x)
                s.close()

            if self.gbuffy:
                data = {}
                data['type'] = 'Buffered data'
                a = self.gbuffy[0]
                data['value'] = self.gbuffy[0]
                self.gbuffy.pop(0)
                x = pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', 8500 + self.id))
                s.sendall(x)
                s.close()
                if self.gbuffy:
                    if self.gbuffy[0][1] != a[0][1]:
                        data = {}
                        data['type'] = 'Handover complete'
                        data['value'] = a[1]
                        x = pickle.dumps(data)
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect(('127.0.0.1', 8500 + self.id))
                        s.sendall(x)
                        s.close()

            if 1 in self.inpos:
                hit = [i for i, value in enumerate(self.inpos) if value == 1]
                if hit:
                    for t in range(len(hit)):
                        yy = [item for item in self.buffd if item[1] == hit[t]]
                        if yy:
                            for jj in yy:
                                hp = [item for item in yy if jj == item[0]]
                                if hp:
                                    if len(set(hp)) == hp[0][4]:
                                        hp.sort(key=lambda x: x[2])
                                        pj = [i for i, value in enumerate(self.buffd) if value[0] == jj]
                                        self.buffd = [i for j, i in enumerate(self.buffd) if j not in pj]
                                        data = {}
                                        data['type'] = 'Data Carrier'
                                        data['value'] = hp
                                        # hp = []
                                        x = pickle.dumps(data)
                                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                        s.connect(('127.0.0.1', 4000 + int(data['value'][0][1])))
                                        s.sendall(x)
                                        s.close()

    def run1(self):
        t = []
        t1 = threading.Thread(target=self.l_sgw)
        t2 = threading.Thread(target=self.send)
        t3 = threading.Thread(target=self.l_mme)
        t4 = threading.Thread(target=self.l_data)
        t5 = threading.Thread(target=self.l_sig)
        t1.start()
        t3.start()
        t2.start()
        t4.start()
        t5.start()
        t.append(t1)
        t.append(t2)
        t.append(t3)
        t.append(t4)
        t.append(t5)

        for n in t:
            n.join()
