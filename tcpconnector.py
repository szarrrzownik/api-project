# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 00:47:14 2019

@author: Marcin Wujkowski
"""
import socket
import hashlib
import time
import threading
import ast

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST1 = '192.168.100.20'
PORT1 = 49152


def stripper(trg, strp): #string type, #string content
    
    if trg == 'n': #nonce
        noncedist = (strp.find(b'<Nonce>') + 7)
        nonce = repr(strp[noncedist:(noncedist+ 16)])[2:-1] #cutting out the nonce
        
        return nonce
    
    elif trg == 's': #sessionid
        sessioniddist = (strp.find('<CamCtl SessionID='))+19
        sessionid = strp[sessioniddist:(sessioniddist+3)]
        
        return sessionid
        
    elif trg == 'f': #ndfil check vals
        ndfildist = (strp.find('<CamCtl>'))+18
        ndfi = int(strp[ndfildist:(ndfildist+1)])
        print(ndfi)

        return ndfi
    else:
        ...
        
def md5(nonce):
    
    HA1 = hashlib.md5(("UX1803"+":MovieRemote:"+"transmitIT2018").encode('utf-8')).hexdigest()
    AUTENTH = hashlib.md5((HA1+":"+str(nonce)).encode('utf-8')).hexdigest()
    
    return AUTENTH
    
def auth():
    
    soc.send(b'<P2Control><Login>UX1803</Login></P2Control>')
    RESPONSE1 = soc.recv(1024)
    if b"<Nonce>" in RESPONSE1:
        a1=md5(stripper('n', RESPONSE1))
        return a1   
    else:
        ...

def establish():
    
    soc.connect((HOST1, PORT1))

    establisher = 0
    
    while not establisher == 2:
        authstr = auth()
    
        if establisher == 0:
            soc.send(bytes('<P2Control><Auth>'+ authstr + '</Auth><Query Type="env"/></P2Control>', 'utf-8'))
        elif establisher == 1:
            soc.send(bytes('<P2Control><Auth>' + authstr + '</Auth><SessionID></SessionID><CamCtl>$Connect:=On</CamCtl><CamCtl>$MyName:ssAGApp_iOS_Ver.01.01</CamCtl></P2Control>', 'utf-8'))
        else:
           ...  

        RESPONSE2 = repr(soc.recv(1024))[2:-1]
        
        if '<ModelName>' in RESPONSE2:
            establisher = 1
        elif '$MyName:sAG-UX180' in RESPONSE2:
            establisher = 2 
            a2 =stripper('s', RESPONSE2)
        else:
            ...

        print(RESPONSE2)
        
    return a2

def irs(val):
    
    authstr = auth()
    if val == 0:
        val = '?'
    elif val != 0:
        val = "="+str(val)
    else:
        ...
    soc.send(bytes('<P2Control><Auth>'+authstr+'</Auth><SessionID>' +str(sessionid)+ '</SessionID><CamCtl>$Irs:'+ str(val) + '</CamCtl></P2Control>', 'utf-8'))
    RESPONSE2 = repr(soc.recv(1024))[2:-1]
    print(RESPONSE2)
    
def ped(val):
    
    authstr = auth()
    if val <= -151 or val >= 151:
        val = '?'
    elif val >= -150 and val <= 150:
        val = '='+str(val)
    else:
        ...#logs.write(datetime.datetime.now() + ' pedestal failure: value incorrect') 
    soc.send(bytes('<P2Control><Auth>'+str(authstr)+'</Auth><SessionID>'+str(sessionid)+'</SessionID><CamCtl>$MPed:'+ str(val) +'</CamCtl></P2Control>', 'utf-8'))
    RESPONSE2 = repr(soc.recv(1024))[2:-1]
    print(RESPONSE2)

def gain(val): 
    
    authstr = auth()
    if val > 0:
        val = '+' + str(val)
    elif val < 0:                   
        val = str(val)
        #logs.write(datetime.datetime.now() + ' gain failure: value incorrect') 
        ...
    soc.send(bytes('<P2Control><Auth>'+str(authstr)+'</Auth><SessionID>'+str(sessionid)+'</SessionID><CamCtl>$MGain:'+val+'</CamCtl></P2Control>', 'utf-8')) 
    RESPONSE2 = repr(soc.recv(1024))[2:-1]
    print(RESPONSE2)
                
def rgain(val):
    
    authstr = auth()
    if val <= -31 or val >= 31:
        val = '?'
    elif val >= -30 and val <= 30:                   
        val = '='+str(val)
    else:
        #logs.write(datetime.datetime.now() + ' red gain failure: value incorrect') 
        ...
    soc.send(bytes('<P2Control><Auth>'+str(authstr)+'</Auth><SessionID>'+str(sessionid)+'</SessionID><CamCtl>$RGain:'+str(val)+'</CamCtl></P2Control>', 'utf-8')) 
    RESPONSE2 = repr(soc.recv(1024))[2:-1]
    print(RESPONSE2)

def bgain(val):
    
    authstr = auth()
    if val <= -31 or val >= 31:
        val = '?'
    elif val >= -30 and val <= 30:                   
        val = '='+str(val)
    else:
        #logs.write(datetime.datetime.now()+ ' blue gain failure: value incorrect')
        ...
    soc.send(bytes('<P2Control><Auth>'+str(authstr)+'</Auth><SessionID>'+str(sessionid)+'</SessionID><CamCtl>$BGain:'+str(val)+'</CamCtl></P2Control>', 'utf-8')) 
    RESPONSE2 = repr(soc.recv(1024))[2:-1]
    print(RESPONSE2)

def ndfil(): # returns val ,  check vals
    authstr = auth()
    soc.send(bytes('<P2Control><Auth>'+str(authstr)+'</Auth><SessionID>'+str(sessionid)+'</SessionID><CamCtl>$NdFil:?</CamCtl></P2Control>', 'utf-8')) 
    RESPONSE2 = repr(soc.recv(1024))[2:-1]
    RESPONSE2 = stripper('f', RESPONSE2)
    return RESPONSE2

def bars(val): # 0 - off, 1 - on, else - status
    
    authstr = auth()
    if val != 0 and val != 1:
        val = '?'
    elif val == 0:                
        val = '=Off'
    elif val == 1:
        val = '=On'
    else:
        ...#logs.write(datetime.datetime.now()+' bars failure: value incorrect')

    soc.send(bytes('<P2Control><Auth>'+str(authstr)+'</Auth><SessionID>'+str(sessionid)+'</SessionID><CamCtl>$BarSw:'+val+'</CamCtl></P2Control>', 'utf-8')) 
    RESPONSE2 = repr(soc.recv(1024))[2:-1]
    print(RESPONSE2)
    

sessionid = establish()

class Gainval():
    def __init__(self):
        self.gainv = 0
    def sgain(self): #status gain
        
        usoc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        HOST2 = '192.168.100.2'
        PORT2 = 49153
        
        usoc.bind((HOST2, PORT2))

        while True:
            
            RESPONSE3, addr = usoc.recvfrom(2048)
            RESPONSE3 = RESPONSE3.hex()         
            print(RESPONSE3)
        
            if len(RESPONSE3) >= 50:
                gval = int(RESPONSE3[90:92], 16)
                
                print(gval)
                if gval == 0 and RESPONSE3[-10:-8] == str(90):
                    gval = '-100'
                    print(gval)
                    
                else:
                    ...
                self.gainv= gval 
            else:
                ...

            
    
g1 = Gainval()
mythread = threading.Thread(target=g1.sgain).start()
time.sleep(1)
print(g1.gainv)
ndstate = 0
irsstate = 0
gain(1)
time.sleep(1)
for i in range(5):
    time.sleep(1)
    gain(1)













