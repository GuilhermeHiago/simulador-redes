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
 
def find_node(who_search, node, subnet):
    # print("finder")
    # print(subnet)
    node = [x for x in subnet.keys() if get_subnet(x) == get_subnet(who_search.ip_prefix)]
    # print(subnet)
    node = subnet[node[0]]
    # print("no:", node)
    for n in node:
        if n.ip_prefix == who_search.ip_prefix:
            return n
 
    return None