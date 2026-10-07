#!/usr/bin/env python3
import argparse,select,socket,struct,threading

def exact(s,n):
 d=b''
 while len(d)<n:
  x=s.recv(n-len(d))
  if not x: raise ConnectionError()
  d+=x
 return d

def relay(a,b):
 try:
  while 1:
   r,_,_=select.select([a,b],[],[],300)
   if not r:return
   for s in r:
    d=s.recv(65536)
    if not d:return
    (b if s is a else a).sendall(d)
 except OSError:pass
 finally:
  for s in (a,b):
   try:s.close()
   except OSError:pass

def client(c,user,pwd):
 u=None
 try:
  v,n=struct.unpack('!BB',exact(c,2)); methods=exact(c,n)
  if v!=5 or 2 not in methods:c.sendall(b'\x05\xff');return
  c.sendall(b'\x05\x02'); v,n=struct.unpack('!BB',exact(c,2)); name=exact(c,n).decode(); n=exact(c,1)[0]; pw=exact(c,n).decode()
  if v!=1 or name!=user or pw!=pwd:c.sendall(b'\x01\x01');return
  c.sendall(b'\x01\x00'); v,cmd,_,at=struct.unpack('!BBBB',exact(c,4))
  if v!=5 or cmd!=1:raise ValueError()
  if at==1:host=socket.inet_ntoa(exact(c,4))
  elif at==3:host=exact(c,exact(c,1)[0]).decode('idna')
  elif at==4:host=socket.inet_ntop(socket.AF_INET6,exact(c,16))
  else:raise ValueError()
  port=struct.unpack('!H',exact(c,2))[0];u=socket.create_connection((host,port),20);c.sendall(b'\x05\x00\x00\x01'+b'\0'*6);relay(c,u)
 except (OSError,ValueError,UnicodeError,struct.error,ConnectionError):
  try:c.sendall(b'\x05\x01\x00\x01'+b'\0'*6)
  except OSError:pass
 finally:
  c.close()
  if u:
   try:u.close()
   except OSError:pass

def main():
 p=argparse.ArgumentParser();p.add_argument('--listen');p.add_argument('--port',type=int);p.add_argument('--username');p.add_argument('--password');a=p.parse_args();s=socket.socket(socket.AF_INET6);s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.setsockopt(socket.IPPROTO_IPV6,socket.IPV6_V6ONLY,0);s.bind(('::',a.port));s.listen(128);print(f'SOCKS5 listening on {a.listen}:{a.port}',flush=True)
 while 1:
  c,_=s.accept();threading.Thread(target=client,args=(c,a.username,a.password),daemon=True).start()
main()
