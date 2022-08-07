import threading
import numpy as np
import socket
import time
import pickle
import random
import matplotlib.pyplot as plt
import math as m

class user_g(threading.Thread):

    def __init__(self,id,loc,time,n1):

        threading.Thread.__init__(self)

        self.id=id

        self.loc=loc

        self.time=time

        self.enodbs=list(range(n1))

        self.start=1#start

        self.ack_back=[]#ack ro va nakarde pass mifreste

        self.p_sig=[i+5000 for i in self.enodbs]

        self.p_data=[i+6000 for i in self.enodbs]


    def l_sig(self):


        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1',3000+self.id))
        sock.listen(10)


        while True:

            connection, client_address = sock.accept()

            while True:



                data1 = connection.recv(1024);


                if data1 :


                    kc=pickle.loads(data1)

                    if kc['type']=='User Registration2':

                        self.ceb=kc['value']


                if not data1:

                    break;




        return

    def l_data(self):


        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1',4000+self.id))
        sock.listen(10)



        while True:


            connection, client_address = sock.accept()

            while True:


                data1 = connection.recv(1024);


                if data1 :


                    kc=pickle.loads(data1)

                    if kc['type']=='Create Session':

                        self.ack_back.append((kc['value'][0],kc['value'][1]))

                    if kc['type']=='Data Carrier':

                        print('I am '+str(self.id)+' i receive from '+str(kc['value'][0][0])+'\n')
                        for u in range(len(kc['value'])):

                            print(kc['value'][u][3]+'\n')



                if not data1:

                    break;




        return

    def send_data(self):




        while True:



            if self.ack_back:


                data={};

                data['type']="Create Session Ack"
                data['value']=self.ack_back[0]
                self.ack_back.pop(0)
                x=pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1',6000+self.ceb))
                s.sendall(x)
                s.close()


        return


    def send_loc1(self):



        self.start=1
        data={};

        data['type']="Position announcement"

        data['value']=self.id,self.loc[0]

        x=pickle.dumps(data)

        for i in range(len(self.enodbs)):

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1',self.p_sig[i]))
            s.sendall(x)
            s.close()
            if i==len(self.enodbs):
                self.start=1


        if self.start==1:

            for j in range(len(self.loc)):
                data={};

                data['type']="My Location"
                data['value']=self.id,self.loc[j]
                x=pickle.dumps(data)
                for i in range(len(self.enodbs)):

                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect(('127.0.0.1',self.p_sig[i]))
                    s.sendall(x)
                    s.close()

                if j<len(self.time):

                    time.sleep(self.time[j])

        return


    def run1(self):


        t=[]
        t1=threading.Thread(target=self.l_data)
        t2=threading.Thread(target=self.send_data)
        t3=threading.Thread(target=self.l_sig)
        t4=threading.Thread(target=self.send_loc1)

        t2.start()
        t1.start()
        t3.start()
        t4.start()

        t.append(t1)
        t.append(t2)
        t.append(t3)
        t.append(t4)


        for n in t:


            n.join()



class user_f(threading.Thread):

    def __init__(self,id,loc,time,n,rec,delay,file):

        threading.Thread.__init__(self)

        self.id=id

        self.loc=loc

        self.time=time

        self.delay=delay


        file1 = open(file, 'r')
        lines = file1.readlines()

        for i in range(len(lines)-1):
            lines[i]=lines[i][0:len(lines[i])-1]

        self.file=lines

        self.enodbs=list(range(n))

        self.data=0#start baraye ferestadan data

        self.rec=rec#girande

        self.sack1=0#register enod

        self.sack2=0#register enod

        self.start=0#start car

        self.p_sig=[i+5000 for i in self.enodbs]

        self.p_data=[i+6000 for i in self.enodbs]




    def l_sig(self):


        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1',3000+self.id))
        sock.listen(10)


        while True:


            connection, client_address = sock.accept()

            while True:

                data1 = connection.recv(1024);


                if data1 :


                    kc=pickle.loads(data1)

                    if kc['type']=='User Registration2':

                        self.ceb=kc['value']

                        if self.sack2!=1:

                            self.sack1=1



                if not data1:

                    break;

        return

    def l_data(self):


        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1',4000+self.id))
        sock.listen(10)



        while True:

            connection, client_address = sock.accept()

            while True:


                data1 = connection.recv(1024);


                if data1 :


                    kc=pickle.loads(data1)

                    if kc['type']=='Create Session Ack':

                        self.data=1



                if not data1:

                    break;


        return

    def send_data(self):


        kn=0
        while True:



            if self.sack1==1 and self.sack2==0:

                self.sack2=1

                data={};

                data['type']="Create Session"
                data['value']=self.id,self.rec
                x=pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1',6000+self.ceb))
                s.sendall(x)
                s.close()


            if self.data==1:


                while True:



                    data={};
                    data['type']="Data Carrier"
                    data['value']=(self.id,self.rec,kn,self.file[kn],len(self.file))
                    x=pickle.dumps(data)
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect(('127.0.0.1',self.p_data[self.ceb]))
                    s.sendall(x)
                    s.close()
                    if kn==len(self.file)-1:
                        break
                    time.sleep(self.delay[kn])
                    kn=kn+1




        return


    def send_loc1(self):


        time.sleep(0.3)
        self.start=1
        data={};

        data['type']="Position announcement"

        data['value']=self.id,self.loc[0]

        x=pickle.dumps(data)

        for i in range(len(self.enodbs)):

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1',self.p_sig[i]))
            s.sendall(x)
            s.close()
            if i==len(self.enodbs):
                self.start=1


        if self.start==1:

            for j in range(len(self.loc)):


                data={};

                data['type']="My Location"

                data['value']=self.id,self.loc[j]
                x=pickle.dumps(data)

                for i in range(len(self.enodbs)):


                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect(('127.0.0.1',self.p_sig[i]))
                    s.sendall(x)
                    s.close()

                if j<len(self.time):

                    time.sleep(self.time[j])

        return


    def run1(self):


        t=[]


        t1=threading.Thread(target=self.l_data)
        t2=threading.Thread(target=self.send_data)
        t3=threading.Thread(target=self.l_sig)
        t4=threading.Thread(target=self.send_loc1)

        t2.start()
        t1.start()
        t3.start()
        t4.start()

        t.append(t1)
        t.append(t2)
        t.append(t3)
        t.append(t4)


        for n in t:


            n.join()
