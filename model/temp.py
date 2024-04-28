import psutil

def list_interfaces():
    interfaces = psutil.net_if_addrs()
    num_interfaces = len(interfaces)
    print("Number of interfaces on your computer:", num_interfaces)
    print("Names of interfaces:")
    for interface_name in interfaces:
        print("-", interface_name)
    return num_interfaces

num_interfaces = list_interfaces()
