#!/usr/bin/env python3
import argparse
from ZoneManager import ZoneManager


def run():
    parser = argparse.ArgumentParser(description='Command line interface to interact with OVH',
                                     epilog='Run \'ovh-cli COMMAND --help\' for more information on a command.')
    sp = parser.add_subparsers(title='Available commands', metavar='COMMAND', dest='command')

    domain_sp = configure_domain_parsers(sp)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()

    if args.command == 'domain':
        execute_domain(args, domain_sp)


def configure_domain_parsers(sub_parsers):
    parser = sub_parsers.add_parser('domain',
                                    help='Manage domain\'s records',
                                    description='Manage domain\'s records',
                                    epilog='Run \'ovh-cli domain COMMAND --help\' for more information on a command.')
    sub_parser = parser.add_subparsers(title='Available commands', metavar='COMMAND', dest='domain_command')

    add_parser = sub_parser.add_parser('add', help='Add a record to the zone')
    add_parser.add_argument('-z', '--zone', type=str, help='zone name', required=True)
    add_parser.add_argument('-d', '--domain', type=str, help='domain name', required=True)
    add_parser.add_argument('-n', '--hostname', type=str, help='hostname to infer ipv4 and ipv6')
    add_parser.add_argument('-a', '--api', help='add api sub domain', action='store_true')
    add_parser.add_argument('-4', '--ipv4', type=str, help='the ipv4 address')
    add_parser.add_argument('-6', '--ipv6', type=str, help='the ipv6 address')

    delete_parser = sub_parser.add_parser('delete', help='Delete an existing record from the zone')
    delete_parser.add_argument('-z', '--zone', type=str, help='zone name', required=True)
    delete_parser.add_argument('-d', '--domain', type=str, help='domain name', required=True)
    delete_parser.add_argument('-n', '--hostname', type=str, help='hostname to infer ipv4 and ipv6')
    delete_parser.add_argument('-a', '--api', help='delete api sub domain', action='store_true')
    delete_parser.add_argument('-4', '--ipv4', type=str, help='the ipv4 address')
    delete_parser.add_argument('-6', '--ipv6', type=str, help='the ipv6 address')

    list_parser = sub_parser.add_parser('list', help='List all zone\'s records')
    list_parser.add_argument('-z', '--zone', type=str, help='zone name', required=True)

    return parser


def execute_domain(args, parser):
    if args.domain_command is None:
        parser.print_help()
        return

    if args.domain_command == 'add' or args.domain_command == 'delete':
        zone_manager = ZoneManager(args.zone)
        ipv4_address, ipv6_address = None, None
        if args.ipv4 is not None:
            ipv4_address = args.ipv4
        if args.ipv6 is not None:
            ipv6_address = args.ipv6
        if args.hostname is not None:
            (ipv4_address, ipv6_address) = zone_manager.get_hostname_ips(args.hostname)
            print(f'Hostname: {args.hostname}, ipv4: {ipv4_address}, ipv6: {ipv6_address}')

        if args.domain_command == 'add':
            print(f'Adding domain: {args.domain}, ipv4: {ipv4_address}, ipv6: {ipv6_address}, api: {args.api}')
            zone_manager.add_domain(args.domain, ipv4_address, ipv6_address, args.api)

        if args.domain_command == 'delete':
            print(f'Deleting domain: {args.domain}, ipv4: {ipv4_address}, ipv6: {ipv6_address}, api: {args.api}')
            zone_manager.delete_domain(args.domain, ipv4_address, ipv6_address, args.api)

    if args.domain_command == 'list':
        zone_manager = ZoneManager(args.zone)
        zone_manager.dump_all_domains()


if __name__ == "__main__":
    run()
