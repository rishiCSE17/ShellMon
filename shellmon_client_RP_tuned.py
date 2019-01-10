'''
    +---------------------+
    | Module Description  |
    +---------------------+
    Res_Collect : Resource Collection module
    collects system information such as CPU, Memory, Storage & Bandwidth
    using CAP Theorem (SDN RFC), extending it to include Bandwidth Utilization
    normalize with linear eqn z = W_1*C + W_2*M + W_3*S + W_4*B  (for all W_i : user specific)
    returns the normalised value to the invoking module

    +-----------------------+
    | Copyright Information |
    +-----------------------+
    ALl right reserved to, Mr. Saptarshi Ghosh
    Ph.D. research fellow, London Southbank University, London, UK
    Developed for BlueArch Orchastrator, under SONNET project


    [NOTE] install following for python 2.7
        * apt -y install python-gi-cairo python python-pip pythdon-dev
        * pip install psutil matplotlib drawnow pymysql
'''

import psutil
import time
import matplotlib.pyplot as plt
import sqlite3
from drawnow import *
import datetime
import time
import random
import pymysql
import os


z_list = []
cpu_list = []
mem_list = []
bat_list = []
nw_list = []
sto_list = []
plt.ion()

db_conn=None
db_cur=None

def myplot():
    plt.ylim(0, 1000)
    plt.title('ShellMon System Information')
    plt.grid(True)
    plt.ylabel('Utilization')
    plt.xlabel('Time')

    plt.plot(z_list, 'o-', label='Z_Value')
    plt.plot(cpu_list, 'o-', label='CPU Utilization')
    plt.plot(mem_list, 'o-', label='Memory Utilization')
    plt.plot(nw_list, 'o-', label='Bandwidth Utilization')
    plt.legend(loc='upper left')


''' Sqlite Functions BEGAIN '''

def db_connect(host,un,pw,db,port):
    global db_conn
    db_conn=pymysql.connect(host=host, port=port, db=db, user=un, passwd=pw)
    #global db_cur
    #db_cur=db_conn.cursor()


def create_tab():
    global db_cur
    db_cur = db_conn.cursor()
    db_cur.execute("CREATE TABLE IF NOT EXISTS local_info (ip varchar(15), \
                                                        mac varchar(20), \
                                                        _timestamp REAL, \
                                                        _datestamp varchar(40), \
                                                        cpu REAL, \
                                                        core_count REAL, \
                                                        memory REAL, \
                                                        Storage REAL, \
                                                        bw_util REAL, \
                                                        z_val REAL )"
                )
    db_cur.close()

def clear_db():
    global db_cur
    db_cur = db_conn.cursor()
    db_cur.execute("delete from local_info")
    db_cur.close()

def insert_data(ip, mac, ts, ds, cpu, core, mem, sto, bw, z_val):
    global db_cur
    db_cur = db_conn.cursor()
    db_cur.execute("INSERT INTO local_info VALUES('" +
                ip + "', '" +
                mac + "', " +
                str(ts) + ",'" +
                ds + "'," +
                str(cpu) + "," +
                str(core) + "," +
                str(mem) + "," +
                str(sto) + "," +
                str(bw) + "," +
                str(z_val) + ")"
                )
    db_conn.commit()
    db_cur.close()
    # cur.close()
    # conn.close()


''' sqlite Functions END '''

def  _iterator(intf):
    while True:
        '''cpu utilization percent'''
        per_util_cpu = psutil.cpu_percent(interval=True)

        '''core count'''
        core_count_cpu = psutil.cpu_count(logical=True)

        '''free memory percent'''
        per_util_mem = psutil.virtual_memory().percent

        '''free storage percent'''
        per_util_disk = psutil.disk_usage('/').percent

        '''Network Utilization percent'''
        time_quanta = 3
        if_name = intf #list(psutil.net_if_stats().keys())[0]
        #if if_name == 'lo':
            #if_name = list(psutil.net_if_stats().keys())[1]
        nic_speed = psutil.net_if_stats()[if_name][2]  # get(if_name).speed
        if nic_speed == 0 :
            nic_speed=100
        r_byte_1 = psutil.net_io_counters(pernic=True).get(if_name).bytes_recv
        s_byte_1 = psutil.net_io_counters(pernic=True).get(if_name).bytes_sent
        time.sleep(time_quanta)
        r_byte_delta = int(psutil.net_io_counters(pernic=True).get(if_name).bytes_recv) - int(r_byte_1)
        s_byte_delta = int(psutil.net_io_counters(pernic=True).get(if_name).bytes_sent) - int(s_byte_1)
        byte_per_sec = (r_byte_delta + s_byte_delta) / time_quanta
        per_util_nic = (byte_per_sec * 100 / (nic_speed * 2 ** 17)) 
        print(byte_per_sec)
        print (per_util_nic)

        ''' Battery Remaining'''
        bat = psutil.sensors_battery()
        if bat == None:
            per_remian_berrty = 100
        else:
            per_remian_berrty = bat.percent

        '''Z function calculation'''
        #z_val = (core_count_cpu / 8) * per_util_cpu + per_util_mem + per

        '''
        print('CPU Utilization      : ', per_util_cpu)
        print('CPU Core             : ', core_count_cpu)
        print('Memory Utilization   : ', per_util_mem)
        print('Storage Utilization  : ', per_util_disk)
        print('Network Utilization  : ', per_util_nic)
        print('Battery Remaining    : ', per_remian_berrty)
        '''
        cpu_list.append(per_util_cpu * core_count_cpu)
        mem_list.append(per_util_mem)
        bat_list.append(per_remian_berrty)
        nw_list.append(per_util_nic * 8)
        sto_list.append(per_util_disk)

        z_val = per_util_cpu * core_count_cpu + per_util_mem + per_util_disk + 8 * per_util_nic + (100 - per_remian_berrty)

        # Timestamp & Datestamp calculation
        ts = time.time()
        ds = str(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))

        '''
            ip & mac address
        '''
        #ip = psutil.net_if_addrs()[if_name][0][1]
        cmd_ip="temp=`ifconfig wlan0 | grep inet | head -1` ; echo $temp | cut -d ' ' -f2 "
        #cmd_ip="ifconfig wlan0 | grep 'inet addr' | cut -d ':' -f2 | cut -d ' ' -f1"
        ip=os.popen(cmd_ip).read().rstrip()
        #mac = psutil.net_if_addrs()[if_name][1][1]
        cmd_mac="temp=`ifconfig wlan0 | grep ether | head -1` ; echo $temp | cut -d ' ' -f2 "
        #cmd_mac="x=`ifconfig wlan0 | grep 'HWaddr'` ; echo $x | cut -d ' ' -f5"
        mac=os.popen(cmd_mac).read().rstrip()

        insert_data(ip, mac, ts, ds, per_util_cpu, core_count_cpu, per_util_mem, per_util_disk, 8 * per_util_nic, z_val)

        z_list.append(z_val)
        if z_list.__len__() > 100:
            z_list.__delitem__(0)
        print('ip: ', ip, ' mac: ', mac, ' Z_Val:  ', z_val, '\t @ ', ds)
        drawnow(myplot)


def main():
    host='10.1.2.101' #raw_input('Enter the IP address of MySQL server : ')
    port=3306 #int(input('Enter the port number (default 3306) : '))
    uname='root' #input('Enter User name : ')
    pw='password' #input('Enter password : ')
    db='Flow_Schema' #input('Enter schema name : ')
    intf='wlan0' #raw_input('enter interface name : ')
    db_connect(host='10.1.2.101',port=6633,un='rishi',pw='Password123..',db='flow_schema')
    # init_db('shellmon')
    create_tab()
    clear_db()
    _iterator(intf)

main()
