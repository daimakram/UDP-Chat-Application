'''
This module defines the behaviour of server in your Chat Application
'''
import sys
import getopt
import socket
import util
import threading
import queue
import time
import random

q_dic={}
class Server:
    '''
    This is the main Server Class. You will to write Server code inside this class.
    '''
    def __init__(self, dest, port, window):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(None)
        self.sock.bind((self.server_addr, self.server_port))
        self.window = window
        self.dict_add={}
        self.dict_bool={}
        self.cli=""
    
    def chunk_converter( self, msg_join, g):
            global q_dic
            seq=random.randint(0, 1000)
            pac = [msg_join[i : i+util.CHUNK_SIZE] for i in range(0, len(msg_join), util.CHUNK_SIZE)]
            packet_join = util.make_packet("start", seq)
            self.sock.sendto(packet_join.encode("utf-8"), g)
            i = 0
            for i in range(0, len(pac)):
                c = (q_dic[g]).get()
                if c[0] == "ack" and int(c[1]) == seq + i + 1:
                    packet_j = util.make_packet("data",seq +i + 1, pac[i])
                    print(pac[i])
                    self.sock.sendto(packet_j.encode("utf-8"), g)
            d = (q_dic[g]).get()
            if d[0] == "ack" and int(d[1]) == seq + i + 2:
                packet_e = util.make_packet("end", seq + i + 2)
                self.sock.sendto(packet_e.encode("utf-8"), g)
            e = (q_dic[g]).get()
            if e[0] == "ack" and int(e[1]) == seq + i + 3:
                return True
        
    def message_ack(self,msg_client,addl_client):
        global q_dic
        c = (q_dic[addl_client]).get()
        if c[0] == "ack":
            (q_dic[addl_client]).put(c)
            return False
        p = c[0]
        seq = int(c[1])
        l1 = ""
        if p == "start":
            m = util.make_packet("ack", seq+1)
            self.sock.sendto(m.encode("utf-8"), addl_client)
            seq = seq+1
            while True:
                d = (q_dic[addl_client]).get()
                r = int(d[1])
                if d[0] == "end":
                    m = util.make_packet("ack", r + 1)
                    self.sock.sendto(m.encode("utf-8"),addl_client)
                    break
                elif d[0] == "data" and r == seq:
                    l1 = l1 + d[2]
                    m = util.make_packet("ack", r + 1)
                    self.sock.sendto(m.encode("utf-8"), addl_client)
                    seq = r + 1
        return l1
    def client_handler(self,msg_client,addl_client):
        global q_dic
        while True:
            l1 = self.message_ack(msg_client, addl_client)
            if(not l1):
                continue
            t = l1.split(" ")
            msgType = t[0]
            user = self.Key_from_val(addl_client)
            num = len(self.dict_add)
            if(msgType == "join"):
                if(num == 10):
                    err1 = util.make_message("err_server_full", 2)
                    self.chunk_converter(err1, addl_client)
                    q_dic.pop(addl_client)
                    return
                if(t[2] in self.dict_add.keys()):
                    err2 = util.make_message("err_username_unavailable", 2)
                    self.chunk_converter(err2, addl_client)
                    q_dic.pop(addl_client)
                    return
                user = t[2]
                self.dict_add[user] = addl_client
                self.dict_bool[user] = "joined"
                print("join:", user) 
            elif(msgType == "send_message"):
                    list_send = []
                    number = t[2]    
                    for i in range(3, 3 + int(number)):
                        list_send.append(t[i])
                    tit=t[3 + int(t[2]):]
                    m = " "
                    msg_send = m.join(tit)
                    i = 0
                    sad = True
                    list_b = {}
                    for i in range(0, int(number)):
                        if sad:
                            print("msg:",user)
                            sad = False
                        if list_send[i] in self.dict_add.keys():
                            if list_send[i] in list_b.keys() and list_b[list_send[i]] == True:
                                continue
                            ni=user + " "+ msg_send
                            msg_make_up = util.make_message("forward_message", 4, ni)
                            self.chunk_converter(msg_make_up,self.dict_add[list_send[i]])
                            list_b[list_send[i]] = True
                        else:
                            print("msg:", user, "to non-existent user", list_send[i])
            elif(msgType == "request_users_list"):
                    print("request_users_list:", user)
                    an = ""
                    a = " "
                    i = 0
                    for value in self.dict_add.keys():
                        an = an+value+a
                        i = i+1
                    ans = str(i)+" "+an
                    msg1 = util.make_message("response_users_list", 3, ans)
                    self.chunk_converter(msg1, addl_client)
            elif(msgType == "send_file"):
                if(not (self.Check_int(t[2]))):
                    self.unk_error(user, addl_client)
                    return
                no_of_clients = t[2]    
                leng = int(t[1])
                d = t[3:3+int(t[2])]
                file_name = t[3+int(t[2])]
                q = t[2:4+int(t[2])]
                p = " "
                r = len(p.join(q))
                file_content = l1[-(leng-r-1):]
                if(l1 == file_content):
                    file_content = ""
                i = 0
                sad = True
                d_bool = {}
                for i in range(0, int(no_of_clients)):
                    if sad:
                        print("file:", user)
                        sad=False
                    if d[i] in self.dict_add.keys():
                        if d[i] in d_bool.keys() and d_bool[d[i]] == True:
                            continue
                        file_for=str(1)+ " " + user+ " "+ file_name+ " " +file_content
                        print(file_for)
                        file_for_up = util.make_message("forward_file", 4, file_for)
                        self.chunk_converter(file_for_up,self.dict_add[d[i]])
                        d_bool[d[i]] = True
                    else:
                        print("file:", user, "to non-existent user", d[i])    
            elif(msgType == "disconnect"):
                print("disconnected:", user)
                self.dict_add.pop(user)
                self.dict_bool.pop(user)
                return
          
    def start(self):
        '''
        Main loop.
        continue receiving messages from Clients and processing it
        '''
        global q_dic
        while True:
            msg_client,addl_client = self.sock.recvfrom(11000)
            pack_ty,seq_no,l1,_ = util.parse_packet(msg_client.decode("utf-8"))
            if pack_ty == "start" and addl_client not in self.dict_add.values():
                p=[pack_ty, seq_no, l1]
                q=queue.Queue()
                q_dic[addl_client] = q
                (q_dic[addl_client]).put(p)
                t1 = threading.Thread(target=self.client_handler, args=(msg_client, addl_client))
                t1.start()
            elif pack_ty == "start" and addl_client in self.dict_add.values():
                p = [pack_ty,seq_no,l1]
                (q_dic[addl_client]).put(p)
            elif pack_ty == "data" or pack_ty == "ack" or pack_ty == "end":
                p = [pack_ty,seq_no,l1]
                (q_dic[addl_client]).put(p)
                
            
                
                
                
    def Key_from_val(self,add):
        for key, val in self.dict_add.items():
            if add == val:
                return key
    def unk_error(self,user,addl_client):
        erro=util.make_message("err_unknown_message",2)
        self.chunk_converter(erro,addl_client)
        print("disconnected:", "sent unknown command")
        self.dict_add.pop(user)
        self.dict_bool.pop(user)
    def Check_int(self,d):
        try: 
            int(d)
            return True
        except ValueError:
            return False
                            
                        
                    
                  

        
                        
                    
                
                

        
        
    #raise NotImplementedError

# Do not change this part of code

if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our module completion
        '''
        print("Server")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW | --window=WINDOW The window size, default is 3")
        print("-h | --help Print this help")

    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "p:a:w", ["port=", "address=","window="])
    except getopt.GetoptError:
        helper()
        exit()

    PORT = 15000
    DEST = "localhost"
    WINDOW = 3

    for o, a in OPTS:
        if o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW = a

    SERVER = Server(DEST, PORT,WINDOW)
    try:
        SERVER.start()
        t=threading.Thread(target=SERVER)
    except (KeyboardInterrupt, SystemExit):
        exit()
