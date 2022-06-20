from operator import sub
import sys
from dataclasses import dataclass, field
from typing import List
from Node import Node
from Router import Router
from util import *
 
 
# uma mensagem de solicitação de resposta do ICMP é enviada ao destinatário pela fonte;
# o programa do ping define um identificador de sequência e recebe essas mensagens de solicitação de resposta;
# o ping insere o horário de envio na seção de dados da mensagem e então envia uma mensagem de resposta de eco ICMP de volta à fonte. Se o host estiver ativo ele a recebe;
# o horário da chegada da resposta é registrado por meio do ping, que já contabilizou o horário de envio para cálculo do tempo de ida e volta da mensagem;
# ele incrementa o identificador de sequência e envia uma nova mensagem de solicitação de resposta, de forma continuada, até completar o número de envios solicitado pelo usuário;
# o programa é encerrado.
def ping(origem:Node, destino:Node):
    # se origem nao sabe ender destino
        # caso seja na mesma subrede -> arp p/ destino -> icmp p/ destino
        # caso outra subrede -> arp p/ router -> icmp p/ router repassar
    origem.send_icmp_echo_request(origem, destino, 8)
    pass    


def traceroute(origem:Node, destino:Node):
    ttl = 1

    while(True):
        resp = origem.send_icmp_echo_request(origem, destino, ttl)

        if resp == True:
            ttl += 1
        else:
            break

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
 
node_index = lines.index("#NODE") if "#NODE" in lines else -1
router_index = lines.index("#ROUTER") if "#ROUTER" in lines else -1
table_index = lines.index("#ROUTERTABLE") if "#ROUTERTABLE" in lines else -1
 
nodes : List[Node] = []
routers : List[Router] = []
 
# create nodes
for i in range(node_index+1, router_index):
    data = lines[i].split(",")
    nodes.append(Node(data[0], data[1], data[2], data[3]))
 
# create routers
for i in range(router_index+1, table_index):
    data = lines[i].split(",")
 
    ip_list = []
    mac_list = []
 
    for i in range(int(data[1])):
        mac_list.append(data[2])
        ip_list.append(data[3])
 
        del data[2:4]
 
    ports = []
    # table[data[0]] = []
 
    temp_router = Router(data[0], data[1], mac_list, ip_list)

    for i in range(len(ip_list)):
        ports.append( Node(data[0], mac_list[i], ip_list[i], ip_list[i]))
        nodes.append(ports[i])
        ports[i].router_ref = temp_router
        ports[i].is_router_port = True
        ports[i].router_port = ports[i]

    temp_router.port_list = ports
    
    routers.append(temp_router)
 
# connect nodes to node
for n in nodes:
    n.net = nodes

# table = {}
# create router tables
for i in range(table_index+1, len(lines)):
    data = lines[i].split(",")

    r = [x for x in routers if x.router_name == data[0]][0]
    
    values = data[1:]

    # netdest/prefix : [nexthop(ip), port]
    r.router_table[values[0]] = [values[1], values[2]]

a = '19.2.2.0'
a2 = '19.2.2.1'
 
 
for r in routers:
    for port in r.ip_list:
        r.nodes_ref[port] = []
 
        for node in nodes:
            if node.gateway == port[0:port.index("/")]:
                r.nodes_ref[port] = r.nodes_ref[port] + [node]
                node.router_ref = r
                node.router_port = [x for x in r.port_list if get_subnet(x.ip_prefix) == get_subnet(node.ip_prefix)][0]

for r in routers:
    r.global_nodes = nodes
# arp_request_intra(nodes[0], nodes[1])

# nodes[0].send_arp(nodes[1])

traceroute(nodes[0], nodes[1])
# nodes[0].send_icmp_echo_request(nodes[0], nodes[1], 8)

# nodes[0].send_icmp_echo_request(nodes[0], nodes[1], 8)
# nodes[0].send_icmp_echo_request(nodes[0], nodes[2], 2)
# routers[0].port_list[0].send_arp(nodes[2])


# routers[0].send_arp(nodes[2])
 
# TIME EXICED MORRE AO CHEGAR A 0

# simulador <topologia> <comando> <origem> <destino>
# python3 simulador.py topologia.txt ping n1 n2
# python simulador.py topologia.txt ping n1 n2