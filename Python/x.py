import struct
from  mutils import *
u=3020
#u=hex(u)
u=f'{u:x}'
print(u)
u="%s%s" %(u[2:],u[:2])
u=int(u,16)
print(u)

