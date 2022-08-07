import threading
import numpy as np
import socket
import time
import pickle
import random
import matplotlib.pyplot as plt
import math as m

from class_eNodeB import *
from class_sgw import *
from class_users import *
from class_mme import *


class Network:


    def __init__(self,n1,n2,loc):

        self.n1=n1

        self.n2=n2

        self.loceb=loc

        self.thread=[]

        self.user=[]



    def init_network(self):

        s1=MME(self.n1,self.n2)
        t1=threading.Thread(target=s1.run1)
        t1.start()
        self.thread.append(t1)


        s2=SGW(self.n1,self.n2)
        t2=threading.Thread(target=s2.run1)
        t2.start()
        self.thread.append(t2)

        for i in range(self.n1):
            sp=eNodeB(i,self.loceb[i],self.n2)
            t1=threading.Thread(target=sp.run1)
            t1.start()
            self.thread.append(t1)


    def add_user(self,id,loc,time,delay):

        self.user.append((id,loc,time,delay))


    def connection_request(self, sender_id, receiver_id, file_name):

        k1=[(item[0],item[1],item[2],self.n1,receiver_id,item[3]) for item in self.user if sender_id==item[0]]

        k2=[(item[0],item[1],item[2],self.n1) for item in self.user if receiver_id==item[0]]

        s1=user_f(k1[0][0],k1[0][1],k1[0][2],k1[0][3],k1[0][4],k1[0][5],file_name)
        s2=user_g(k2[0][0],k2[0][1],k2[0][2],k2[0][3])


        t1=threading.Thread(target=s1.run1)
        t2=threading.Thread(target=s2.run1)
        t2.start()
        t1.start()
        self.thread.append(t2)
        self.thread.append(t1)


    def run(self):

        for n in self.thread:


            n.join()
