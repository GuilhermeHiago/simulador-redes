from operator import sub
import sys
from dataclasses import dataclass, field
from typing import List

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

def get_subnet(ip_mask):
    mask = int(ip_mask[ip_mask.find("/")+1:])
    # ip = ip_mask[0:ip_mask.find("/")]

    bites = []

    while "." in ip_mask:
        bites.append( int(ip_mask[0:ip_mask.find(".")]) )
        ip_mask = ip_mask[ip_mask.find(".")+1:]

    bites.append( int(ip_mask[0:ip_mask.find("/")]) )

    mask_value = '1'*mask + '0'*(32-mask)

    mask_value = [int(mask_value[0:8], 2), int(mask_value[8:16], 2), int(mask_value[16:24], 2), int(mask_value[24:32], 2)]

    for i in range(len(mask_value)):
        mask_value[i] = bites[i] & mask_value[i]

    return mask_value



@dataclass
class Node:
    name : str
    mac : str
    ip_prefix : str
    gateway : str

    router_ref = None
    arp_table = {}
    router_port = None

    def send_arp(self, destino):
        # caso o arp seja dentro da subrede
        if get_subnet(self.ip_prefix) == get_subnet(destino.ip_prefix):
            subnet = [x for x in self.router_ref.nodes_ref.keys() if get_subnet(x) == get_subnet(self.ip_prefix)]

            subnet = self.router_ref.nodes_ref[subnet[0]]

            if destino.ip_prefix not in self.arp_table.keys():
                print(f"Note over {self.name} : ARP Request<br/>Who has {destino.ip_prefix[0:destino.ip_prefix.find('/')]}? Tell {self.ip_prefix[0:self.ip_prefix.find('/')]}")
                # "enviando" arp request para todos da subrede
                for n in subnet:
                    # envia arp para todos da rede
                    resp = n.receive_arp(self, destino)

                    if resp != None:
                        self.arp_table[destino.ip_prefix] = resp
                        return

        self.send_arp_router()
        # # caso destino em subrede externa passa para roteador
        # else:

        return None

    def send_arp_router(self):
        resp = self.router_port.receive_arp(self, self.router_port)
        
        self.arp_table[self.router_port.ip_prefix] = resp

    def receive_arp(self, origem, destino):
        if self.ip_prefix != origem.ip_prefix and get_subnet(self.ip_prefix) == get_subnet(origem.ip_prefix) and self.ip_prefix == destino.ip_prefix:
            print(f"{destino.name} ->> {origem.name} : ARP Reply<br/>{destino.ip_prefix[0:destino.ip_prefix.find('/')]} is at {destino.mac}")
            return destino.mac

        return None

@dataclass
class Router:
    router_name : str
    num_ports : str
    mac_list : List[str]
    ip_list : List[str]

    port_list : List[Node] = field(default_factory=lambda: [])

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


@dataclass
class RouteTable:

    @dataclass
    class RouteTableElement:
        name : str
        net_dest : str
        nexthop : str
        port : str

    table : List[RouteTableElement]


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
table = RouteTable([])

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

    for i in range(len(ip_list)):
        ports.append( Node(data[0], mac_list[i], ip_list[i], ip_list[i]))
    
    routers.append(Router(data[0], data[1], mac_list, ip_list, ports))

for i in range(table_index+1, len(lines)):
    data = lines[i].split(",")
    endereco = RouteTable.RouteTableElement(data[0], data[1], data[2], data[3])
    table.table.append(endereco)

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

nodes[0].send_arp(nodes[1])
print("\n")
routers[0].send_arp(nodes[2])

# print("porta: ", nodes[0].router_port)
# print("\n")
# nodes[0].send_arp_router()

# print(routers[0].port_list)
# simulador <topologia> <comando> <origem> <destino>
# python3 simulador.py topologia.txt ping n1 n2