from operator import sub
import sys
from dataclasses import dataclass, field
from typing import List
from Node import Node
from util import *
 
 
@dataclass
class Router:
    router_name : str
    num_ports : str
    mac_list : List[str]
    ip_list : List[str]
 
    port_list : List[Node] = field(default_factory=lambda: [])
 
    router_table = {}
 
    arp_table = {}
 
    nodes_ref = {}
 
    def send_arp(self, destino):
        port = None
 
        for p in self.port_list:
            if get_subnet(p.ip_prefix) == get_subnet(destino.ip_prefix):
                port = p
                break
 
        if destino.ip_prefix not in port.arp_table.keys():
            print(f"Note over {port.name} : ARP Request<br/>Who has {destino.ip_prefix[0:destino.ip_prefix.find('/')]}? Tell {port.ip_prefix[0:port.ip_prefix.find('/')]}")
 
 
        # da problema o port nao possui
        # port.send_arp(destino)
        # print(self.nodes_ref)
        for i in self.nodes_ref[port.ip_prefix]:
            i.receive_arp(port, destino)
 
        pass
 
    def receive_arp(port, origem, destino):
        if destino == port:
            return mac_list[ ip_list.find(destino.ip_list) ]
        pass
 
 
# router_table = {'ip': {'mac':None, 'port':None}}
 
 
def arp_request_intra(origem, destino):
    # Note over n1 : ARP Request<br/>Who has 192.168.0.3? Tell 192.168.0.2
    # n2 ->> n1 : ARP Reply<br/>192.168.0.3 is at 00:00:00:00:00:02
    # n1 ->> n2 : ICMP Echo Request<br/>src=192.168.0.2 dst=192.168.0.3 ttl=8
    # n2 ->> n1 : ICMP Echo Reply<br/>src=192.168.0.3 dst=192.168.0.2 ttl=8
    
    if destino.ip_prefix not in origem.arp_table.keys():
        print(f"Note over {origem.name} : ARP Request<br/>Who has {destino.ip_prefix[0:destino.ip_prefix.find('/')]}? Tell {origem.ip_prefix[0:origem.ip_prefix.find('/')]}")
        # "enviando" arp request para todos da subrede
        for n in nodes:
            # caso encontrou
            if origem.ip_prefix != n.ip_prefix and get_subnet(origem.ip_prefix) == get_subnet(n.ip_prefix) and n.ip_prefix == destino.ip_prefix:
                print(f"{destino.name} ->> {origem.name} : ARP Reply<br/>{destino.ip_prefix[0:destino.ip_prefix.find('/')]} is at {destino.mac}")
                return destino.mac
 
    return None
 
def arp_request_extra(origem, destino):
    if destino.ip_prefix not in origem.arp_table.keys():
        print(f"Note over {origem.name} : ARP Request<br/>Who has {destino.ip_prefix[0:destino.ip_prefix.find('/')]}? Tell {origem.ip_prefix[0:origem.ip_prefix.find('/')]}")
    
 
    pass
 
def arp(origem, destino):
    if get_subnet(origem.ip_prefix) == get_subnet(destino):
        return arp_request_intra(origem, destino)
    else:
        # arp_request_extra(origem, destino)
        pass
 
# uma mensagem de solicitação de resposta do ICMP é enviada ao destinatário pela fonte;
# o programa do ping define um identificador de sequência e recebe essas mensagens de solicitação de resposta;
# o ping insere o horário de envio na seção de dados da mensagem e então envia uma mensagem de resposta de eco ICMP de volta à fonte. Se o host estiver ativo ele a recebe;
# o horário da chegada da resposta é registrado por meio do ping, que já contabilizou o horário de envio para cálculo do tempo de ida e volta da mensagem;
# ele incrementa o identificador de sequência e envia uma nova mensagem de solicitação de resposta, de forma continuada, até completar o número de envios solicitado pelo usuário;
# o programa é encerrado.
def ping(origem, destino):
    # se origem nao sabe ender destino
        # caso seja na mesma subrede -> arp p/ destino -> icmp p/ destino
        # caso outra subrede -> arp p/ router -> icmp p/ router repassar
    pass    
 
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
 
 
nodes = []
routers = []
table = {}
 
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
    table[data[0]] = []
 
    for i in range(len(ip_list)):
        ports.append( Node(data[0], mac_list[i], ip_list[i], ip_list[i]))
    
    routers.append(Router(data[0], data[1], mac_list, ip_list, ports))
 
 
for i in range(table_index+1, len(lines)):
    data = lines[i].split(",")
    table[data[0]].append({data[1]: {'next_hop': data[2], 'port': data[3]}})
 
 
 
print("router")
for r in routers: 
    for p in r.port_list: print(p)
 
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
 
 
# arp_request_intra(nodes[0], nodes[1])
 
nodes[0].send_arp(nodes[0].router_ref.port_list[0])
print(nodes[0].name, nodes[0].arp_table)
print(nodes[0].router_ref.port_list[0].name, nodes[0].router_ref.port_list[0].arp_table)
print("\n")
routers[0].send_arp(nodes[2])
 
# print("porta: ", nodes[0].router_port)
# print("\n")
# nodes[0].send_arp_router()
 
# TIME EXICED MORRE AO CHEGAR A 0
 
# print(routers[0].port_list)
# simulador <topologia> <comando> <origem> <destino>
# python3 simulador.py topologia.txt ping n1 n2
# python simulador.py topologia.txt ping n1 n2
 

