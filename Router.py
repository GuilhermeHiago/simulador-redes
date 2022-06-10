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
 
    def receive_arp(self, port, origem, destino):
        if destino == port:
            return self.mac_list[ self.ip_list.find(destino.ip_list) ]
        pass