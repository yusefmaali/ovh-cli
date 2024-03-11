import argparse
import logging
import sys

from ovh_cli.account import Account
from ovh_cli.zone_manager import ZoneManager


class OvhCli:
    _logger: logging.Logger
    _args: argparse.Namespace
    _account_subparser: argparse.ArgumentParser
    _domain_subparser: argparse.ArgumentParser
    _config_path: str | None

    def __init__(self):
        self._logger = logging.getLogger("OvhCli")
        self._config_path = None

    @classmethod
    def run_cli(cls) -> bool:
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        ovh_cli = OvhCli()
        ovh_cli.run()
        return True

    def run(self) -> None:
        parser = argparse.ArgumentParser(
            description='Command line interface to interact with OVH',
            epilog='Run \'ovh-cli COMMAND --help\' for more information on a command.')

        parser.add_argument('-c', '--config', type=str, help='path to ovh.conf file')

        sp = parser.add_subparsers(
            title='Available commands',
            metavar='COMMAND',
            dest='command')

        self._configure_account_parsers(sp)
        self._configure_domain_parsers(sp)

        self._args = parser.parse_args()

        if self._args.command is None:
            parser.print_help()
            return

        if self._args.command == 'domain':
            self._execute_domain()

        if self._args.command == 'account':
            self._execute_account()

    def _configure_domain_parsers(self, sub_parsers) -> None:
        self._domain_subparser = sub_parsers.add_parser(
            'domain',
            help='Manage domain\'s records',
            description='Manage domain\'s records',
            epilog='Run \'ovh-cli domain COMMAND --help\' for more information on a command.')
        sub_parser = self._domain_subparser.add_subparsers(
            title='Available commands',
            metavar='COMMAND',
            dest='domain_command')

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

    def _configure_account_parsers(self, sub_parsers) -> None:
        self._account_subparser = sub_parsers.add_parser(
            'account',
            help='Manage the account',
            description='Manage the account',
            epilog='Run \'ovh-cli account COMMAND --help\' for more information on a command.')
        sub_parser = self._account_subparser.add_subparsers(
            title='Available commands',
            metavar='COMMAND',
            dest='account_command')

        sub_parser.add_parser('greetings', help='Log a greeting message')
        sub_parser.add_parser('register', help='Register new consumer_key')

    def _execute_domain(self) -> None:
        if self._args.domain_command is None:
            self._domain_subparser.print_help()
            return

        if self._args.domain_command == 'add' or self._args.domain_command == 'delete':
            zone_manager = ZoneManager(self._args.zone, config_file=self._args.config)
            ipv4_address, ipv6_address = None, None
            if self._args.ipv4 is not None:
                ipv4_address = self._args.ipv4
            if self._args.ipv6 is not None:
                ipv6_address = self._args.ipv6
            if self._args.hostname is not None:
                (ipv4_address, ipv6_address) = zone_manager.get_hostname_ips(self._args.hostname)
                self._logger.info('Hostname: %s, ipv4: %s, ipv6: %s',
                                  self._args.hostname, ipv4_address, ipv6_address)

            if self._args.domain_command == 'add':
                self._logger.info('Adding domain: %s, ipv4: %s, ipv6: %s, api: %s',
                                  self._args.domain, ipv4_address, ipv6_address, self._args.api)
                zone_manager.add_domain(self._args.domain, ipv4_address, ipv6_address, self._args.api)

            if self._args.domain_command == 'delete':
                self._logger.info('Deleting domain: %s, ipv4: %s, ipv6: %s, api: %s',
                                  self._args.domain, ipv4_address, ipv6_address, self._args.api)
                zone_manager.delete_domain(self._args.domain, ipv4_address, ipv6_address, self._args.api)

        if self._args.domain_command == 'list':
            zone_manager = ZoneManager(self._args.zone, config_file=self._args.config)
            zone_manager.dump_all_domains()

    def _execute_account(self) -> None:
        if self._args.account_command is None:
            self._account_subparser.print_help()
            return

        if self._args.account_command == 'greetings':
            account = Account(config_file=self._args.config)
            account.greetings()

        if self._args.account_command == 'register':
            account = Account(config_file=self._args.config)
            account.consumer_key_create_request()

            ckr = account.consumer_key_request
            Account.register_endpoints(ckr)
            ZoneManager.register_endpoints(ckr)

            validation_url, consumer_key = account.consumer_key_complete_registration()

            self._logger.info('Please visit %s to authenticate the request', validation_url)
            input('Press Enter to continue...')
            self._logger.info('The consumerKey is: %s', consumer_key)
            self._logger.info('Follow the README instructions and store it in the ovh.conf file')

            account.greetings()


run_cli = OvhCli.run_cli
