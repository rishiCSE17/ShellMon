import pymysql
import time
import os
import matplotlib.pyplot as plt
from drawnow import *
import matplotlib.animation as anim

db_conn = None
db_cur = None

fig=plt.figure()

class node_mon:
    def __init__(self,ip):
        self.ip=ip
        self.lst_z=[]
    def add_z(self, z_val):
        self.lst_z.append(z_val)
        if len(self.lst_z) > 50:
            self.lst_z.pop(0)
    def get_ip(self):
        return self.ip
    def get_z_list(self):
        return self.lst_z
    def create_plot(self):
        self.xs=[]
        for i in range(0,len(self.lst_z)):
            self.xs.append(i)
        self.ys=self.lst_z
        return self.xs, self.ys


def create_subplot():
    k=1
    plt.title('ShellMon Server Moving Average Information')
    plt.grid(True)
    plt.ylabel('Utilization')
    plt.xlabel('Time')
    for ip in dict_node_mon.keys():
        x,y=dict_node_mon.get(ip).create_plot()
        #if x != [] and y != []:
            #print('graph lists')
        print(ip)
        print(x)
        print(y)
        plt.plot(x,y,'o-',label=ip)
        k+=1
    plt.legend(loc='upper left')


dict_node_mon={}

def db_connect(host, port, uname, passwd, schema):
    global db_conn
    db_conn = pymysql.connect(host=host, port=int(port), user=uname, passwd=passwd, db=schema)


def db_clear(host, port, uname, passwd, schema):
    db_connect(host, port, uname, passwd, schema)
    qstr = "delete from flow_schema.local_info"
    global db_cur
    db_cur = db_conn.cursor()
    db_cur.execute(qstr)
    db_cur.close()
    db_conn.commit()
    db_conn.close()


def fetch(host, port, uname, passwd, schema):
    while True:
        db_connect(host, port, uname, passwd, schema)
        qstr = "select    ip, mac, avg(z_val) " \
               "from      flow_schema.local_info " \
               "group by  ip " \
               "order by  ip"

        global db_cur
        db_cur = db_conn.cursor()
        db_cur.execute(qstr)
        os.system('cls')
        for row in db_cur:
            ip=row[0]
            avg_z_val=row[2]
            if ip not in dict_node_mon:
                dict_node_mon.update({ip : node_mon(ip)})
            else:
                dict_node_mon.get(ip).add_z(avg_z_val)
                #print(dict_node_mon.get(ip).get_ip())
                #print(dict_node_mon.get(ip).get_z_list())

        db_cur.close()
        db_conn.close()
        #create_subplot()
        drawnow(create_subplot)
        time.sleep(3)


if __name__ == '__main__':
    host = input('Enter MySQL server IP address : ')
    port = 3306 #input('Enter poer number (default 3306) : ')
    uname = 'rishi' #input('Enter username : ')
    passwd = input('Enter passowd : ')
    schema = 'flow_schema' #input('Enter schema name : ')

    choice = input('\n\n\t\t Do you want to reset the database ? (y/n)...')
    if choice == 'y':
        db_clear(host, port, uname, passwd, schema)

        fetch(host, port, uname, passwd, schema)

