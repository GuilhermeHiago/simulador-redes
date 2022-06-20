from dataclasses import dataclass, field
from util import *

@dataclass
class Node:
    name : str
    mac : str
    ip_prefix : str
    gateway : str
 
    net = []

    router_ref = None
    arp_table : dict = field(default_factory=lambda: {})
    router_port = None

    is_router_port = False
 
    def send_arp(self, destino):

        # caso o arp seja dentro da subrede
        if get_subnet(self.ip_prefix) == get_subnet(destino.ip_prefix):
            print(f"Note over {self.name} : ARP Request<br/>Who has {destino.ip_prefix[0:destino.ip_prefix.find('/')]}? Tell {self.ip_prefix[0:self.ip_prefix.find('/')]}")

            # subnet = [x for x in self.router_ref.nodes_ref.keys() if get_subnet(x) == get_subnet(self.ip_prefix)]
            # subnet = self.router_ref.nodes_ref[subnet[0]]

            subnet = [x for x in self.net if get_subnet(x.ip_prefix) == get_subnet(self.ip_prefix)]
 
            if destino.ip_prefix not in self.arp_table.keys():
                # "enviando" arp request para todos da subrede
 
                resp = list(map(lambda n : n.receive_arp(self, destino), subnet))
                # clean resp - removing None returns
                resp = [x for x in resp if x]

                if resp[0] not in [None, []]:
                    self.arp_table[destino.ip_prefix] = [resp[0], destino]
                    return [resp[0], destino]

        #caso porta do roteador
        if self.is_router_port:
            return [self.router_ref.get_nexthop(destino), destino]

        print(f"Note over {self.name} : ARP Request<br/>Who has {self.router_port.ip_prefix[0:self.router_port.ip_prefix.find('/')]}? Tell {self.ip_prefix[0:self.ip_prefix.find('/')]}")
        return self.send_arp_router()
            
        # # caso destino em subrede externa passa para roteador
 
    def send_arp_router(self):
        resp = self.router_port.receive_arp(self, self.router_port)
        self.arp_table[self.router_port.ip_prefix] = [resp, self.router_port]

        return [resp, self.router_port]
 
    def receive_arp(self, origem, destino):
        if self.ip_prefix != origem.ip_prefix and get_subnet(self.ip_prefix) == get_subnet(origem.ip_prefix) and self.ip_prefix == destino.ip_prefix:
            print(f"{destino.name} ->> {origem.name} : ARP Reply<br/>{destino.ip_prefix[0:destino.ip_prefix.find('/')]} is at {destino.mac}")
            
            self.arp_table[origem.ip_prefix] = [origem.mac, origem]

            # self.mac == destino.mac
            return self.mac
 
        return None
 
 
    def send_icmp_echo_request(self, origem, destino, ttl):
        address : Node = None

        to_router = get_subnet(destino.ip_prefix) != get_subnet(self.ip_prefix)
        know_router_mac = self.router_port.ip_prefix in self.arp_table

        # if self.is_router_port and to_router:
        #     self.router_ref.get_nexthop(destino)

        # caso de fora da rede e sabe onde esta o router
        if to_router and know_router_mac:
            address = self.arp_table[self.router_port.ip_prefix][1]
        
        # caso nao sabe posiçao mas e na rede
        elif destino.ip_prefix not in self.arp_table and not (to_router and know_router_mac):
            address = (self.send_arp(destino))[1]

        # caso sabe posiçao
        else:
            address = self.arp_table[destino.ip_prefix][1]

        # n1 ->> r1 : ICMP Echo Request<br/>src=192.168.0.2 dst=192.168.1.2 ttl=8
        ip_origem = origem.ip_prefix[0:origem.ip_prefix.find('/')]
        ip_destino = destino.ip_prefix[0:destino.ip_prefix.find('/')]

        print(f"{self.name} ->> {address.name} : ICMP Echo Request<br/>src={ip_origem} dst={ip_destino} ttl={ttl}")

        return address.receive_icmp_echo_request(self, origem, destino, ttl)
 
    def send_icmp_time_exceeded(self, who_send, origem, destino, ttl):
        address : Node = None

        to_router = get_subnet(destino.ip_prefix) != get_subnet(self.ip_prefix)
        know_router_mac = self.router_port.ip_prefix in self.arp_table

        if self.is_router_port and to_router and not know_router_mac:
            address = self.router_ref.get_nexthop(destino)

        elif to_router and know_router_mac:
            address = self.arp_table[self.router_port.ip_prefix][1]
        elif destino.ip_prefix not in self.arp_table:
            address = (self.send_arp(destino))[1]
        else:
            address = self.arp_table[destino.ip_prefix][1]

        # r1 ->> n1 : ICMP Time Exceeded<br/>src=160.10.128.1 dst=160.10.128.10 ttl=8
        ip_origem = origem.ip_prefix[0:origem.ip_prefix.find('/')]
        ip_destino = destino.ip_prefix[0:destino.ip_prefix.find('/')]

        print(f"{self.name} ->> {address.name} : ICMP Time Exceeded<br/>src={ip_origem} dst={ip_destino} ttl={ttl}")

        return address.receive_icmp_time_exceeded(self, origem, destino, ttl)

    def receive_icmp_time_exceeded(self, who_send, origem, destino, ttl):
        ttl -= 1

        if self.ip_prefix == destino.ip_prefix:
            return True
        
        elif ttl <= 0:
            return False
        elif get_subnet(destino.ip_prefix) != get_subnet(self.ip_prefix):
            return self.router_ref.receive_icmp_time_exceeded(self, origem, destino, ttl)
        else:
            return self.send_icmp_time_exceeded(self, origem, destino, ttl)

    def receive_icmp_echo_request(self, who_send, origem, destino, ttl):
        # se este nodo for destino
        ttl -= 1

        if destino.ip_prefix == self.ip_prefix and ttl >= 0:
            ip_origem = self.ip_prefix[0:self.ip_prefix.find('/')]
            ip_destino = origem.ip_prefix[0:origem.ip_prefix.find('/')]

            """"talvez mudar caminho de volta nem sempre eh o mesmo de chegada"""

            print(f"{self.name} ->> {who_send.name} : ICMP Echo Reply<br/>src={ip_origem} dst={ip_destino} ttl=8")
            
            return who_send.receive_icmp_echo_reply(self, self, origem, 8)
        # time exceeded
        elif ttl <= 0:
            return self.send_icmp_time_exceeded(self, self, origem, 8)#who_send, origem, destino, 8)
        # caso não seja o destino
        elif get_subnet(destino.ip_prefix) != get_subnet(self.ip_prefix):
            if self.is_router_port:
                return self.router_ref.receive_icmp(self, self, origem, destino, ttl)
        pass

    def send_icmp_echo_reply(self, origem, destino, ttl):
        address : Node = None

        to_router = get_subnet(destino.ip_prefix) != get_subnet(self.ip_prefix)
        know_router_mac = self.router_port.ip_prefix in self.arp_table

        if to_router and know_router_mac:
            address = self.arp_table[self.router_port.ip_prefix][1]
        elif destino.ip_prefix not in self.arp_table:
            address = (self.send_arp(destino))[1]
        else:
            address = self.arp_table[destino.ip_prefix][1]

        # n1 ->> r1 : ICMP Echo Request<br/>src=192.168.0.2 dst=192.168.1.2 ttl=8
        ip_origem = origem.ip_prefix[0:origem.ip_prefix.find('/')]
        ip_destino = destino.ip_prefix[0:destino.ip_prefix.find('/')]

        print(f"{self.name} ->> {address.name} : ICMP Echo Reply<br/>src={ip_origem} dst={ip_destino} ttl={ttl}")

        return address.receive_icmp_echo_reply(self, origem, destino, ttl)

    def receive_icmp_echo_reply(self, who_send, origem, destino, ttl):
        # se este nodo for destino
        ttl -= 1

        if destino.ip_prefix == self.ip_prefix and ttl >= 0:
            return
        elif ttl <= 0:
            return self.send_icmp_time_exceeded(who_send, origem, destino, 8)
        # caso não seja o destino
        elif get_subnet(destino.ip_prefix) != get_subnet(self.ip_prefix):
            if self.is_router_port:
                self.router_ref.receive_icmp_reply(self, self, origem, destino, ttl)
        else:
            print("na subnet")
        pass