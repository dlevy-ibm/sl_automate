__author__ = 'dlevy'

#Store all required parameters for a baremetal machine
#after retrieval of the data from Softlayer
class Baremetal:
    def __init__(self, file_info):
        self.node_name = file_info["node_name"]
        self.private_portable_ip = None
        self.private_portable_netmask = None
        self.private_portable_gateway_ip = None
        self.primary_private_ip = None
        self.primary_private_netmask = None
        self.interface_1 = None
        self.interface_2 = None
        self.ucarp_private_portable_ip = None
        self.file_pos = file_info["pos"]

    def to_csv(self):
        str_part1 = "%s,%s,%s," % (self.node_name, self.private_portable_ip, self.private_portable_netmask)
        str_part2 = "%s,%s,%s," % (self.private_portable_gateway_ip, self.primary_private_ip, self.primary_private_netmask)
        str_part3 = "eth%s,eth%s" % (self.interface_1, self.interface_2)
        str_final = str_part1 + str_part2 + str_part3
        if (self.ucarp_private_portable_ip is not None):
            str_final += "," + self.ucarp_private_portable_ip
        return str_final
