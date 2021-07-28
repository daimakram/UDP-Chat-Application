'''
This module defines the behaviour of a client in your Chat Application
'''
import sys
import getopt
import socket
import random
from threading import Thread
import os
import util
import time


'''
Write your code inside this class. 
In the start() function, you will read user-input and act accordingly.
receive_handler() function is running another thread and you have to listen 
for incoming messages in this function.
'''


class Client:
    '''
    This is the main Client Class. 
    '''
    def __init__(self, username, dest, port, window_size):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(None)
        self.sock.bind(('', random.randint(10000, 40000)))
        self.name = username
        self.window = window_size
        self.boole=True
        self.boole2=True
        self.c=""
    def start(self):
        '''
        Main Loop is here
        Start by sending the server a JOIN message.
        Waits for userinput and then process it
        '''
        msg_join = util.make_message("join",1,self.name)
        packet_join = util.make_packet(msg=msg_join)
        self.sock.sendto(packet_join.encode("utf-8"),(self.server_addr,self.server_port))
        to_send=""
        while self.boole2:
            time.sleep(2)
            if(self.c!="err_unknown_message" and self.c!="err_server_full" and self.c!="err_username_unavailable"):
                to_send=input()
            div=to_send.split()
            title=div[0]
            if(title=="msg"):
                msg_send=util.make_message("send_message",4,to_send[4:])
                packet_send=util.make_packet(msg=msg_send)
                self.sock.sendto(packet_send.encode("utf-8"),(self.server_addr,self.server_port))
            elif(to_send=="list"):
                msg1=util.make_message("request_users_list",2)
                l_send=util.make_packet(msg=msg1)
                self.sock.sendto(l_send.encode("utf-8"),(self.server_addr,self.server_port))
            elif(title=="file"):
                file_name=div[-1]
                try:
                    f=open(file_name,'r')
                except FileNotFoundError as e:
                    print(e)
                    continue
                data=f.read()
                d=to_send[5:]+" "+data
                file_send=util.make_message("send_file",4,d)
                packet_file=util.make_packet(msg=file_send)
                self.sock.sendto(packet_file.encode("utf-8"),(self.server_addr,self.server_port))
            elif(to_send=="quit"):
                msg2=util.make_message("disconnect",1,self.name)
                packet_f=util.make_packet(msg=msg2)
                self.sock.sendto(packet_f.encode("utf-8"),(self.server_addr,self.server_port))
                print("quitting")
                self.boole=False
                break
            elif(to_send=="help"):
                print("FORMATS:")
                print("Message: msg <number_of_users> <username1> <username2> … <message>")
                print("Available Users: list")
                print("File Sharing: file <number_of_users> <username1> <username2> … <file_name>")
                print("Quit: quit")
            else:
                print("incorrect userinput format")          
                   
        return
        #raise NotImplementedError
            

    def receive_handler(self):
        '''
        Waits for a message from server and process it accordingly
        '''
        while self.boole:
            msg,add=self.sock.recvfrom(4096)
            _,_,l1,_=util.parse_packet(msg.decode("utf-8"))
            t=l1.split(" ")
            msgType=t[0]
            self.c=msgType
            if(msgType=="response_users_list"):
                no=int(t[2])
                i=0
                l2=[]
                for i in range(3,no+3):
                    l2.append(t[i])
                l3=sorted(l2)
                m=" "
                n=m.join(l3)
                print("list:",n)
            elif(msgType=="forward_message"):
                ni=len(t[2])-int(t[1])
                ts=t[2]+":"
                print("msg:",ts,l1[ni+1:])
            elif(msgType=="forward_file"):
                leng=int(t[1])
                r=t[3]+":"
                print("file:",r,t[4])
                q=t[2:4+int(t[2])]
                fil_name=USER_NAME+"_"+t[4]
                p=" "
                ri=len(p.join(q))
                if(leng-ri-1==0):
                    c=open(fil_name,'a')
                    c.close()
                    continue
                file_c=l1[-(leng-ri-1):]
                c=open(fil_name,'a')
                c.write(file_c)
                c.close()
            elif(msgType=="err_unknown_message"):
                print("diconnected: server received an unknown command")
                self.boole2=False
                break
            elif(msgType=="err_server_full"):
                print("disconnected server full")
                self.boole2=False
                break
            elif(msgType=="err_username_unavailable"):
                print("disconnected: username not available")
                self.boole2=False
                break
        #raise NotImplementedError



#Do not change this part of code
if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our Client module completion
        '''
        print("Client")
        print("-u username | --user=username The username of Client")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW_SIZE | --window=WINDOW_SIZE The window_size, defaults to 3")
        print("-h | --help Print this help")
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "u:p:a:w", ["user=", "port=", "address=","window="])
    except getopt.error:
        helper()
        exit(1)

    PORT = 15000
    DEST = "localhost"
    USER_NAME = None
    WINDOW_SIZE = 3
    for o, a in OPTS:
        if o in ("-u", "--user="):
            USER_NAME = a
        elif o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW_SIZE = a

    if USER_NAME is None:
        print("Missing Username.")
        helper()
        exit(1)

    S = Client(USER_NAME, DEST, PORT, WINDOW_SIZE)
    try:
        # Start receiving Messages
        T = Thread(target=S.receive_handler)
        T.daemon = True
        T.start()
        # Start Client
        S.start()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
