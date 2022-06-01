import sys
from dataclasses import dataclass
from typing import List

@dataclass
class Node:
    name : str
    mac : str
    ipPrefix : str
    gateway : str

@dataclass
class Router:
    router_name : str
    num_ports : str
    MAC0 : str
    ip_list : List[str]

@dataclass
class RouteTable:

    @dataclass
    class RouteTableElement:
        name : str
        net_dest : str
        nexthop : str
        port : str

    table : List[RouteTableElement]

args = sys.argv[1:]

arq = open(args[0], 'r')    # config file name
lines = arq.readlines()
arq.close()

for i in range(len(lines)): lines[i] = lines[i].strip("\n")
for i in range(len(lines)): lines[i] = lines[i].strip(" ")

comando = args[1]   # pig or traceroute

origem = args[2]    # node name
destino = args[3]   # node name

current_class = None

# print(lines)

node_index = lines.index("#NODE") if "#NODE" in lines else -1
router_index = lines.index("#ROUTER") if "#ROUTER" in lines else -1
table_index = lines.index("#ROUTERTABLE") if "#ROUTERTABLE" in lines else -1

print(node_index)
print(router_index)
print(table_index)

for i in lines:
    i = i.strip('\n')

    if "#NODE" in i:
        current_class = 'node'
        print("AQUI")

    if "#ROUTER" in i:
        current_class = 'router'

    if "#ROUTERTABLE" in i:
        current_class = 'table'

    print(i)