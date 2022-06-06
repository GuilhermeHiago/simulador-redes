import sys
from dataclasses import dataclass
from typing import List

@dataclass
class Node:
    name : str
    mac : str
    ip_prefix : str
    gateway : str

@dataclass
class Router:
    router_name : str
    num_ports : str
    mac_list : List[str]
    ip_list : List[str]

    nodes_ref = {}

@dataclass
class RouteTable:

    @dataclass
    class RouteTableElement:
        name : str
        net_dest : str
        nexthop : str
        port : str

    table : List[RouteTableElement]

# find the occurrence of a element in list
def find_occurrence(list, element, occurrence) -> int:
    index = 0

    for i in range(occurrence):
        pos = list.find(element)

        if pos == -1:
            return -1

        index += pos+1
        list = list[pos+1:]
            

    return index-1

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

nodes = []
routers = []
table = RouteTable([])

# create nodes
for i in range(node_index+1, router_index):
    data = lines[i].split(",")
    nodes.append(Node(data[0], data[1], data[2], data[3]))

# create routers
for i in range(router_index+1, table_index):
    data = lines[i].split(",")
    print(data)

    ip_list = []
    mac_list = []

    for i in range(int(data[1])):
        mac_list.append(data[2])
        ip_list.append(data[3])

        del data[2:4]
    
    routers.append(Router(data[0], data[1], mac_list, ip_list))

for i in range(table_index+1, len(lines)):
    data = lines[i].split(",")
    endereco = RouteTable.RouteTableElement(data[0], data[1], data[2], data[3])
    table.table.append(endereco)

a = '19.2.2.0'
a2 = '19.2.2.1'

# print(find_occurrence(a, '.', 3))

# itererate the routers list
for router in routers:

    # iterate the port ips of router
    for ip in router.ip_list:
        router.nodes_ref[ip] = []

        aux = []
        # iterate de list of nodes
        for node in nodes:
            # find nodes conected to the router port
            if node.ip_prefix[0:find_occurrence(node.ip_prefix, ".", 3)] == ip[0:find_occurrence(ip, '.', 3)]:
                aux.append(node)
                router.nodes_ref[ip] = aux#router.nodes_ref[ip].append(node)

print(routers[0].nodes_ref)
# simulador <topologia> <comando> <origem> <destino>
# python3 simulador.py topologia.txt ping n1 n2