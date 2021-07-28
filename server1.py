'''
This module defines the behaviour of server in your Chat Application
'''
import sys
import getopt
import socket
import util
import threading


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
        
    def start(self):
        '''
        Main loop.
        continue receiving messages from Clients and processing it
        '''
        while True:
            msg_client,addl_client=self.sock.recvfrom(4030)
            self.cli=addl_client
            _,_,l1,_=util.parse_packet(msg_client.decode("utf-8"))
            t=l1.split(" ")
            msgType=t[0]
            user= self.Key_from_val(addl_client)
            num=len(self.dict_add)
            if(msgType=="join"):
                if(num==10):
                    err1=util.make_message("err_server_full",2)
                    err_pack=util.make_packet(msg=err1)
                    self.sock.sendto(err_pack.encode("utf-8"),addl_client)
                    continue
                if(t[2] in self.dict_add.keys()):
                    err2=util.make_message("err_username_unavailable",2)
                    err_pack2=util.make_packet(msg=err2)
                    self.sock.sendto(err_pack2.encode("utf-8"),addl_client)
                    continue
                user=t[2]
                self.dict_add[user]=addl_client
                self.dict_bool[user]="joined"
                print("join:",user)  
            elif(msgType=="send_message" and (user in self.dict_bool.keys())):
                list_send=[]
                if(not (self.Check_int(t[2]))):
                    self.unk_error(user)
                    continue
                if(int(t[2])>len(t)-3):
                    self.unk_error(user)
                    continue
                number=t[2]    
                for i in range(3,3+int(number)):
                    list_send.append(t[i])
                tit=t[3+int(t[2]):]
                m=" "
                msg_send=m.join(tit)
                i=0
                sad=True
                for i in range(0,int(number)):
                    if sad:
                        print("msg:",user)
                        sad=False
                    if list_send[i] in self.dict_add.keys():
                        ni=user+" "+msg_send
                        msg_make_up=util.make_message("forward_message",4,ni)
                        pack_send_up=util.make_packet(msg=msg_make_up)
                        self.sock.sendto(pack_send_up.encode("utf-8"),self.dict_add[list_send[i]])
                    else:
                        print("msg:",user,"to non-existent user",list_send[i])
            elif(msgType=="request_users_list" and (user in self.dict_bool.keys())):
                print("request_users_list:",user)
                an=""
                a=" "
                i=0
                for value in self.dict_add.keys():
                    an=an+value+a
                    i=i+1
                ans=str(i)+" "+an
                msg1=util.make_message("response_users_list",3,ans)
                pack_send_lis=util.make_packet(msg=msg1)
                self.sock.sendto(pack_send_lis.encode("utf-8"),addl_client)
            elif(msgType=="send_file" and (user in self.dict_bool.keys())):
                if(not (self.Check_int(t[2]))):
                    self.unk_error(user)
                    continue
                i=0
                for i in range(0,len(t)):
                    if '.' in t[i]:
                        n=i
                        break
                if(int(t[2])!=n-3):
                    self.unk_error(user)
                    continue
                no_of_clients=t[2]    
                leng=int(t[1])
                d=t[3:3+int(t[2])]
                file_name=t[3+int(t[2])]
                q=t[2:4+int(t[2])]
                p=" "
                r=len(p.join(q))
                file_content=l1[-(leng-r-1):]
                if(l1==file_content):
                    file_content=""
                i=0
                sad=True
                for i in range(0,int(no_of_clients)):
                    if d[i] in self.dict_add.keys():
                        file_for=str(1)+" "+user+" "+file_name+" "+file_content
                        file_for_up=util.make_message("forward_file",4,file_for)
                        file_send_up=util.make_packet(msg=file_for_up)
                        self.sock.sendto(file_send_up.encode("utf-8"),self.dict_add[d[i]])
                        if sad:
                            print("file:",user)
                            sad=False
                    else:
                        print("file:",user,"to non-existent user",d[i])    
            elif(msgType=="disconnect" and (user in self.dict_bool.keys())):
                print("disconnected:",user)
                self.dict_add.pop(user)
                self.dict_bool.pop(user)
                
                
                
    def Key_from_val(self,add):
        for key, val in self.dict_add.items():
            if add == val:
                return key
    def unk_error(self,user):
        erro=util.make_message("err_unknown_message",2)
        err_packo=util.make_packet(msg=erro)
        self.sock.sendto(err_packo.encode("utf-8"),self.cli)
        print("disconnected:",user, "sent unknown command")
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
