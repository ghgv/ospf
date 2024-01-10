import pygame
import networkx as nx
import socket

pygame.init()
screen= pygame.display.set_mode((800,400))
pygame.display.set_caption("OSPF version")
image = pygame.image.load("P.png")

import socket
import yaml
json_data={}
G=nx.Graph()


x=0
y=0
px=20
py=0
black = (0,0,0)

routers=[]

class ROUTER():
        
        def __init__(self,router_id,links):
      
                self.router_id=router_id
                self.image=pygame.image.load('P.png').convert()
                myfont = pygame.font.SysFont("arial", 20)
                self.label = myfont.render(router_id, 1, black)
                self.x = 10+px
                self.y = 10+py
                self.links=links

        def __str__(self):
                print()

        def show(self):
                global px,py
                
                screen.blit(self.image, (self.x,self.y))
                screen.blit(self.label, (self.x, self.y+90))



routers=[]

if __name__ == "__main__":
        
        with open('network.json') as f:
                json_data = yaml.load(f)
                #print(json_data)
                for entry in json_data:
                        if entry["LS type"]==2:
                                print( "Router ID:", entry["Link state id"],entry['Attached Routers'])
                                for neighbor in entry['Attached Routers']:
                                        print("Inc: ",neighbor)
                                        if neighbor  in G.nodes:
                                                pass
                                        else:
                                                a=ROUTER(neighbor,entry['Attached Routers'])
                                                print("adding:", neighbor)
                                                G.add_node(neighbor,pos = (px,py))
                                                #G.nodes[neighbor]['pos']=(px,py)
                                                print("Neig %s %d %d " % (neighbor,px,py))
                                                routers.append(a)
                                                px=px+120
                                                py=py+0

                for entry in json_data:
                        if entry["LS type"]==1:
                                for link in entry["peer"]:
                                        #print(link)
                                        if link["Link_type"]=="2":
                                                #print("added")
                                                a = link["Link ID"] 
                                                for entry2 in json_data:
                                                        if entry2["LS type"]==1:
                                                                for link2 in entry2["peer"]:
                                                                        #print(link)
                                                                                if link2["Link_type"]=="2":
                                                                                        #print("added")
                                                                                        b = link["Link ID"]
                                                                                        if a==b and entry["Link state id"] != entry2["Link state id"]:
                                                                                                G.add_edge(entry["Link state id"],entry2["Link state id"],weight=link["Metric:"])


                
                
        while True:
                screen.fill("white")
                
                for ra,rb,rw  in  G.edges(data=True): 
                        if ra in list(G.nodes): 
                                if rb in list(G.nodes):
                                        rax,ray=G.nodes[ra]['pos']
                                        rbx,rby=G.nodes[rb]['pos']
                                        a=int(rax)
                                        b=int(ray)
                                        c=int(rbx)
                                        d=int(rby)
                                        pygame.draw.line(screen, black, [a+78/2, b+86/2], [c+78/2,d+86/2], 5)
                for router in routers:
                        router.show()
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                pygame.quit()
                                quit()
                pygame.display.update()

        

     