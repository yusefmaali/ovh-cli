#!/usr/bin/env python3

from ZoneManager import ZoneManager

if __name__ == '__main__':
    zone_manager = ZoneManager('test.com')

    zone_manager.print_greetings()
    print()
    zone_manager.dump_all_domains()

    (ipv4_address, ipv6_address) = zone_manager.get_hostname_ips('host_name')
    print(f'Host host_name ips ipv4: {ipv4_address}, ipv6: {ipv6_address}')

    # zone_manager.add_domain('test1', ipv4_address, ipv6_address, True)
    # zone_manager.delete_domain('test', ipv4_address, ipv6_address, True)
