import SoftLayer
import userinfo
from baremetal import *



def get_ethernet_type(machine_nfo):
	for networkComponent in machine_nfo["networkComponents"]:
		if (networkComponent["name"] == "eth"):
			ethnum = networkComponent["port"]
			if (ethnum >=0 and ethnum <=3):
				return 0
			if (ethnum >= 4 and ethnum <=7):
				return 1
	raise Exception ("Could not identify the ethernet/bond combination")


def get_private_vlan_id(machine_nfo):
	for vlan in machine_nfo["networkVlans"]:
			if vlan["name"] == "Private Primary":
				return vlan["id"]

#Read fqdn as dict so we can perform a constant time lookup by fqdn
def read_known_machines(filename):
	machines_in_file = {}
	pos = 0
	with open(filename, 'rb') as csvfile:
		for line in csvfile:
			line = line.rstrip()
			linesplit = line.split(',')
			file_info = {}
			file_info["node_name"] = linesplit[0]
			file_info["pos"] = pos
			machines_in_file[linesplit[1]] = file_info
			pos += 1
	return machines_in_file




def create_fqdn_to_id_map(mgr):
	fqdn_id_map = {}
	for device in mgr.list_hardware(mask="id, fullyQualifiedDomainName"):
		fqdn_id_map[device["fullyQualifiedDomainName"]] = device["id"]
	return fqdn_id_map


#Match provided FQDN to Softlayer ID in constant time
def init_machines_with_ids(mgr):
	machines_in_file = read_known_machines("machines.csv")
	fqdn_id_map = create_fqdn_to_id_map(mgr)
	machines = {}
	for machine in machines_in_file:
		if machine in fqdn_id_map:
			machines[fqdn_id_map[machine]] = Baremetal(machines_in_file[machine])
	return machines

def get_private_portable_subnet(vlan_nfo):
	for subnet in vlan_nfo["subnets"]:
		if (subnet["subnetType"] == "SECONDARY_ON_VLAN" and subnet["addressSpace"] == "PRIVATE"):
			return subnet

def get_private_primary_subnet(vlan_nfo):
	for subnet in vlan_nfo["subnets"]:
		if (subnet["subnetType"] == "PRIMARY" and subnet["addressSpace"] == "PRIVATE"):
			return subnet

#Adds a number to the last octet of an IP
def add_num_to_ip(ip, num):
	ip_split = ip.split('.')
	ip_split[-1] = str(int(ip_split[-1]) + num)
	return '.'.join(ip_split)



hardware_mask = "id, hostname, primaryBackendIpAddress, operatingSystem, networkVlans, networkComponents"
machine_add_constant = 10

client = SoftLayer.create_client_from_env(username=userinfo.user, api_key=userinfo.api_key)
hardware_mgr = SoftLayer.HardwareManager(client)
net_mgr = SoftLayer.NetworkManager(client)

machines = init_machines_with_ids(hardware_mgr)
output = open('output.txt', 'w+')
num_machines_identified = 0

for machine_id in machines:

	machine_info = hardware_mgr.get_hardware(hardware_id=machine_id, mask=hardware_mask)
	private_vlan_id = get_private_vlan_id(machine_info)
	vlan_info = net_mgr.get_vlan(vlan_id=private_vlan_id)
	private_portable_subnet_info = get_private_portable_subnet(vlan_info)
	private_primary_subnet_info = get_private_primary_subnet(vlan_info)
	private_portable = private_portable_subnet_info["networkIdentifier"]

	private_portable_ip = add_num_to_ip(private_portable,machine_add_constant + machines[machine_id].file_pos)
	machines[machine_id].private_portable_ip = private_portable_ip
	machines[machine_id].private_portable_netmask = private_portable_subnet_info["netmask"]
	machines[machine_id].primary_private_ip = machine_info["primaryBackendIpAddress"]
	machines[machine_id].primary_private_netmask = private_primary_subnet_info["netmask"]
	machines[machine_id].private_portable_gateway_ip = add_num_to_ip(private_portable, 4)
	if (machines[machine_id].node_name.startswith("controller")):
		machines[machine_id].ucarp_private_portable_ip = add_num_to_ip(private_portable, 7)
	ethernet_type = get_ethernet_type(machine_info)
	if (ethernet_type == 0):
		machines[machine_id].interface_1 = 0
		machines[machine_id].interface_2 = 2
	else:
		machines[machine_id].interface_1 = 4
		machines[machine_id].interface_2 = 6

	output.write(machines[machine_id].to_csv() + "\n")
	num_machines_identified += 1
	print ("Proccessing machine number: " + str(num_machines_identified))


print ("Succesfully identified " + str(num_machines_identified) + " machines")

