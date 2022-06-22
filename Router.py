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
 
    # port_list : List[Node] = field(default_factory=lambda: [])
    port_list : dict = field(default_factory=lambda: {})
 
    router_table : dict = field(default_factory=lambda: {})
 
    arp_table : dict = field(default_factory=lambda: {})
 
    nodes_ref : dict = field(default_factory=lambda: {})

    global_nodes : List[Node] = field(default_factory=lambda: [])

    # usado para encontrar proximo salto
    # def send_arp(self, destino):
    #     port = None
 
    #     for p in self.port_list:
    #         if get_subnet(p.ip_prefix) == get_subnet(destino.ip_prefix):
    #             port = p
    #             break
 
    #     if destino.ip_prefix not in port.arp_table.keys():
    #         print(f"Note over {port.name} : ARP Request<br/>Who has {destino.ip_prefix[0:destino.ip_prefix.find('/')]}? Tell {port.ip_prefix[0:port.ip_prefix.find('/')]}")
 
 
    #     # da problema o port nao possui
    #     # port.send_arp(destino)
    #     for i in self.nodes_ref[port.ip_prefix]:
    #         i.receive_arp(port, destino)
 
    #     pass
 
    # def receive_arp(self, port, origem:Node, destino:Node):
    #     port_ip = ""

    #     # searchs in router table
    #     for ip in self.router_table.keys():
    #         if get_subnet(destino.ip_prefix) == get_subnet(ip):
    #             port_ip = ip


    #     port = list(filter(lambda p : get_subnet(p.ip_prefix) == get_subnet(port_ip), self.port_list))[0]
        
    #     port.send_arp(destino)
    #     pass

    def receive_icmp(self, who_send:Node , port:Node, origem:Node, destino:Node, ttl):
        port_ip = ""
        interface = ""

        was_in_table = False

        # searchs in router table
        for ip in self.router_table.keys():
            if get_subnet(destino.ip_prefix) == get_subnet(ip):
                was_in_table = True
                port_ip = self.router_table[ip][0]
                interface = self.router_table[ip][1]

        if not was_in_table and "0.0.0.0/0" in self.router_table.keys():
            port_ip = self.router_table["0.0.0.0/0"][0]
            interface = self.router_table["0.0.0.0/0"][1]
        
        port = None

        if port_ip == '0.0.0.0':#self.router_table[port_ip][0] == '0.0.0.0':
            port = self.port_list[int(interface)]
        else:
            # find de router port to send the message
            # port = list(filter(lambda p : p.ip_prefix[0:p.ip_prefix.find("/")] == port_ip, self.global_nodes))[0]
            port = self.port_list[int(interface)]

            dest : Node
            dest = list(filter(lambda n : get_subnet(n.ip_prefix) == get_subnet(port.ip_prefix) and port_ip in n.ip_prefix,port.net))[0]
            
            if dest.ip_prefix not in port.arp_table.keys():
                port.send_arp(dest)

            ip_origem = origem.ip_prefix[0:origem.ip_prefix.find('/')]
            ip_destino = destino.ip_prefix[0:destino.ip_prefix.find('/')]

            print(f"{port.name} ->> {dest.name} : ICMP Echo Request<br/>src={ip_origem} dst={ip_destino} ttl={ttl}")
            return dest.receive_icmp_echo_request(port, origem, destino, ttl)
        # port.send_arp(destino)
        return port.send_icmp_echo_request(origem, destino, ttl)

    def receive_icmp_reply(self, who_send:Node , port:Node, origem:Node, destino:Node, ttl):
        port_ip = ""
        interface = ""

        was_in_table = False

        # searchs in router table
        for ip in self.router_table.keys():
            if get_subnet(destino.ip_prefix) == get_subnet(ip):
                was_in_table = True
                port_ip = self.router_table[ip][0]
                interface = self.router_table[ip][1]

        if not was_in_table and "0.0.0.0/0" in self.router_table.keys():
            port_ip = self.router_table["0.0.0.0/0"][0]
            interface = self.router_table["0.0.0.0/0"][1]
        
        port = None

        # caso mesmo roteador
        if port_ip == '0.0.0.0':
            port = self.port_list[int(interface)]
        # caso outro roteador
        else:
            # find de router port to send the message
            # port = list(filter(lambda p : p.ip_prefix[0:p.ip_prefix.find("/")] == port_ip, self.global_nodes))[0]
            port = self.port_list[int(interface)]

            dest : Node
            dest = list(filter(lambda n : get_subnet(n.ip_prefix) == get_subnet(port.ip_prefix) and port_ip in n.ip_prefix,port.net))[0]
            
            if dest.ip_prefix not in port.arp_table.keys():
                port.send_arp(dest)

            ip_origem = origem.ip_prefix[0:origem.ip_prefix.find('/')]
            ip_destino = destino.ip_prefix[0:destino.ip_prefix.find('/')]

            print(f"{port.name} ->> {dest.name} : ICMP Echo Reply<br/>src={ip_origem} dst={ip_destino} ttl={ttl}")
            return dest.receive_icmp_echo_reply(port, origem, destino, ttl)
        
        ip_origem = origem.ip_prefix[0:origem.ip_prefix.find('/')]
        ip_destino = destino.ip_prefix[0:destino.ip_prefix.find('/')]

        # redirect the reply to the right port
        return port.send_icmp_echo_reply(origem, destino, ttl)


    """INSTAVEL"""
    def receive_icmp_time_exceeded(self, who_send, origem, destino, ttl):
        port_ip = ""
        interface = ""

        was_in_table = False

        # searchs in router table
        for ip in self.router_table.keys():
            if get_subnet(destino.ip_prefix) == get_subnet(ip):
                was_in_table = True
                port_ip = self.router_table[ip][0]
                interface = self.router_table[ip][1]

        if not was_in_table and "0.0.0.0/0" in self.router_table.keys():
            port_ip = self.router_table["0.0.0.0/0"][0]
            interface = self.router_table["0.0.0.0/0"][1]
        
        port = None

        if port_ip == '0.0.0.0':#self.router_table[port_ip][0] == '0.0.0.0':
            port = self.port_list[int(interface)]
        else:
            # find de router port to send the message
            port = self.port_list[int(interface)]

            dest : Node
            dest = list(filter(lambda n : get_subnet(n.ip_prefix) == get_subnet(port.ip_prefix) and port_ip in n.ip_prefix,port.net))[0]
            
            if dest.ip_prefix not in port.arp_table.keys():
                port.send_arp(dest)

            # caso criando pacote
            if ttl == 8:
                ip_origem = port.ip_prefix[0:port.ip_prefix.find('/')]
                ip_destino = destino.ip_prefix[0:destino.ip_prefix.find('/')]

                print(f"{port.name} ->> {dest.name} : ICMP Time Exceeded<br/>src={ip_origem} dst={ip_destino} ttl={ttl}")
                return dest.receive_icmp_time_exceeded(port, port, destino, ttl)
            # caso redirecionando pacote
            else: #ttl != 8:
                ip_origem = origem.ip_prefix[0:origem.ip_prefix.find('/')]
                ip_destino = destino.ip_prefix[0:destino.ip_prefix.find('/')]

                print(f"{port.name} ->> {dest.name} : ICMP Time Exceeded<br/>src={ip_origem} dst={ip_destino} ttl={ttl}")
                return dest.receive_icmp_time_exceeded(port, origem, destino, ttl)
        
        return port.send_icmp_time_exceeded(origem, destino, ttl)

    def get_nexthop(self, destino:Node):
        was_in_table = False

        for k in self.router_table.keys():
            if get_subnet(k) == get_subnet(destino.ip_prefix):
                was_in_table = True
                if self.router_table[k][0] == "0.0.0.0":
                    return self.port_list[int(self.router_table[k][1])]

                nexthop = self.router_table[k][0]

                aux = list(filter(lambda n : nexthop in n.ip_prefix, self.global_nodes))[0]
                return aux#self.port_list[int(self.router_table[k][1])]

        if not was_in_table and "0.0.0.0/0" in self.router_table.keys():
            
            nexthop = self.router_table["0.0.0.0/0"][0]

            aux = list(filter(lambda n : nexthop in n.ip_prefix, self.global_nodes))[0]
            return aux