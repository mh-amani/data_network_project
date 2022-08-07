import threading
import numpy as np
import socket
import time
import pickle
import random
import matplotlib.pyplot as plt
import math as m

class MME(threading.Thread):


    def __init__(self,n1,n2):

        threading.Thread.__init__(self)


        self.enodbs=[]

        self.n2=n2

        self.enbs=list(range(n1))

        self.users=list(range(n2))

        self.ack_eb=[0]*n2#ack lazem baraye har user az taraf enodb ha

        self.dis=[99999]*n2#min distance har user

        self.ebu_old=[-10]*n2;

        self.ebu_new=[-1]*n2

        self.enb_p=[i+7000 for i in self.enbs]


    def l_enodb(self,i):


        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1',7500+i))
        sock.listen(10)




        while True:



            connection, client_address = sock.accept()

            while True:



                data1 = connection.recv(1024);


                if data1 :


                    kc=pickle.loads(data1)

                    if kc['type']=="eNodeB-MME connection":


                        self.enodbs.append(kc['value'])



                    if kc['type']=='User distance':

                        self.ack_eb[kc['value'][1]]=self.ack_eb[kc['value'][1]]+1

                        self.dis[kc['value'][1]]=np.minimum(self.dis[kc['value'][1]],kc['value'][2])

                        if kc['value'][2]==np.minimum(self.dis[kc['value'][1]],kc['value'][2]):

                            self.ebu_new[kc['value'][1]]=kc['value'][0]




                if not data1:

                    break;




        return

    def send(self):




        while True:



            if len(self.enbs) in self.ack_eb:

                a=self.ack_eb.index(len(self.enbs))

                self.ack_eb[a]=0
                self.dis[a]=99999

                data={};
                data['type']="Change route"
                data['value']=self.ebu_new[a],self.users[a]
                x=pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                s.connect(('127.0.0.1',9090))
                s.sendall(x)
                s.close()

                data={};
                data['type']="User Registration1"


                data['value']=self.users[a],self.ebu_old[a]
                x=pickle.dumps(data)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                s.connect(('127.0.0.1',7000+self.ebu_new[a]))
                s.sendall(x)
                s.close()




                if self.ebu_old[a]!=-10:

                    data={};
                    data['type']="User deregistration"
                    data['value']=self.users[a]
                    x=pickle.dumps(data)
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    s.connect(('127.0.0.1',7000+self.ebu_old[a]))
                    s.sendall(x)
                    s.close()
                self.ebu_old[a]=self.ebu_new[a]



        return


    def run1(self):


        t=[]

        for j in range(len(self.enbs)):


            t1=threading.Thread(target=self.l_enodb, args=(j,))


            t1.start()
            t.append(t1)


        t2=threading.Thread(target=self.send)
        t2.start()
        t.append(t2)

        for n in t:


            n.join()
