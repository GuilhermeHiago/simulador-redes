from dataclasses import dataclass, field
from util import *

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
 
                # resp = list(map(lambda n : n.receive_arp(self, destino), subnet))
 
                # if resp[0] != None:
                #     self.arp_table[destino.ip_prefix] = resp
                #     return
 
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
            
            self.arp_table[origem.ip_prefix] = origem.mac
            return destino.mac
 
        return None
 
 
    def send_icmp_echo_request(self, origem, destino, ttl):
 
        # n1 ->> r1 : ICMP Echo Request<br/>src=192.168.0.2 dst=192.168.1.2 ttl=8
 
        return None
 
    def receive_icmp(self, origem, destino, ttl):
        # se este nodo for destino
 
        # caso não seja o destino
        pass