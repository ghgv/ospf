
inputs= [("0.0.0.0","0"),
         ("5.6.7.8","1.2.3.4"),
         ("5.6.7.8","1.2.3.4"),
         ("5.6.7.8","1.2.3.4")]

local="1.2.3.4"
table =[{"state": "down",     "DR":"0.0.0.0", "Neigh_seen":"0"     ,"next":"down"},
        {"state": "down",     "DR":"5.6.7.8", "Neigh_seen":local   ,"next":"init"},
        {"state": "init",     "DR":"5.6.7.8", "Neigh_seen":local   ,"next":"ExStart"},
        {"state": "ExStart",  "DR":"5.6.7.8", "Neigh_seen":local   ,"next":"Exchage"},
        ]

def lookUp(state,input):
    (input1,input2)=input
    #print(state,input1,input2)
    for item in table:
        if item["state"]== state and item["DR"]== input1 and item["Neigh_seen"]== input2:
            
            return item["next"]
    return -1



def FSM(state,inputs):
    for input in inputs:
        #print(input)
        state = lookUp(state,input)
        #print(state)
        if state==-1:
            return print("Error occurred")
    print(state)
    return state

FSM("down",inputs)