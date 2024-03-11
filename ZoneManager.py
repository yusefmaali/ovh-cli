import logging

import ovh


class ZoneManager:
    client: ovh.Client
    zone_name: str
    domains: dict

    def __init__(self, zone_name: str):
        self.logger = logging.getLogger("ZoneManager")
        self.client = ovh.Client()
        self.zone_name = zone_name
        self.domains = {}

        self.__cache_all_domains()

    def domain_exists(self, domain_name: str) -> bool:
        """ Check if a domain exists in the zone """
        return domain_name in self.domains

    def get_hostname_ips(self, host_name: str) -> tuple:
        """ Get the ip addresses of the hostname """
        ipv4_address = None
        ipv6_address = None

        records = self.domains.get(host_name)
        if records is None:
            return ipv4_address, ipv6_address

        for record in records:
            field_type = record['fieldType']
            target = record['target']
            if field_type == 'A':
                ipv4_address = target
            elif field_type == 'AAAA':
                ipv6_address = target

        return ipv4_address, ipv6_address

    def dump_all_domains(self):
        """ Dump all domains"""
        keys = list(self.domains.keys())

        super_group_keys = []
        for key in keys:
            if key.startswith('api.') or f'api.{key}' not in keys:
                continue
            super_group_keys.append(key)

        super_groups = {}
        for key in super_group_keys:
            if key in super_groups:
                continue

            api_key = f'api.{key}'
            super_groups[key] = {}

            keys.remove(key)
            super_groups[key][key] = self.domains.get(key)

            keys.remove(api_key)
            super_groups[key][api_key] = self.domains.get(api_key)

        super_group_keys = super_groups.keys()
        sorted(super_group_keys)

        self.logger.info('Grouped domains (%d items)', len(super_group_keys))
        for domain in super_group_keys:
            self.logger.info(str(domain).upper())
            for sub_domain in super_groups[domain]:
                self.logger.info('   %s', sub_domain)
                for entry in super_groups[domain][sub_domain]:
                    field_type = entry['fieldType']
                    target = entry['target']
                    self.logger.info('      %s => %s', field_type, target)
            self.logger.info('')

        self.logger.info('')
        self.logger.info('Other domains')
        for domain in keys:
            if len(domain) == 0:
                self.logger.info("(empty)")
            else:
                self.logger.info(domain)

            for entry in self.domains[domain]:
                field_type = entry['fieldType']
                target = entry['target']
                self.logger.info('      %s => %s', field_type, target)

            self.logger.info('')

    def add_domain(self, domain_name: str, ipv4_address: str, ipv6_address: str, add_api_domain: bool):
        """ Add a test domain
        :param domain_name
        :param ipv4_address
        :param ipv6_address
        :param add_api_domain:
        """
        if not self.domain_exists(domain_name):
            print(f'Adding domain (A) {domain_name} => {ipv4_address}')
            self.client.post(f'/domain/zone/{self.zone_name}/record',
                             fieldType='A', subDomain=domain_name, target=ipv4_address)

            print(f'Adding domain (AAAA) {domain_name} => {ipv6_address}')
            self.client.post(f'/domain/zone/{self.zone_name}/record',
                             fieldType='AAAA', subDomain=domain_name, target=ipv6_address)

        api_domain_name = f'api.{domain_name}'
        if add_api_domain and not self.domain_exists(api_domain_name):
            print(f'Adding domain (A) {api_domain_name} => {ipv4_address}')
            self.client.post(f'/domain/zone/{self.zone_name}/record',
                             fieldType='A', subDomain=api_domain_name, target=ipv4_address)

            print(f'Adding domain (AAAA) {api_domain_name} => {ipv6_address}')
            self.client.post(f'/domain/zone/{self.zone_name}/record',
                             fieldType='AAAA', subDomain=api_domain_name, target=ipv6_address)

        self.client.post(f'/domain/zone/{self.zone_name}/refresh')

    def delete_domain(self, domain_name: str, ipv4_address: str, ipv6_address: str, delete_api_domain: bool):
        """ Delete a domain
        :param domain_name
        :param ipv4_address
        :param ipv6_address
        :param delete_api_domain:
        """
        self.__delete_domain_action(domain_name, ipv4_address, ipv6_address)

        if delete_api_domain:
            api_domain_name = f'api.{domain_name}'
            self.__delete_domain_action(api_domain_name, ipv4_address, ipv6_address)

        self.client.post(f'/domain/zone/{self.zone_name}/refresh')

    def __delete_domain_action(self, domain_name: str, ipv4_address: str, ipv6_address: str):
        """ Call the action to delete a domain.
         Internal method
        :param domain_name
        :param ipv4_address
        :param ipv6_address
        """
        records = self.domains.get(domain_name)
        if records is None:
            return

        for record in records:
            field_type = record['fieldType']
            target = record['target']
            domain_id = record['domainId']
            if (field_type == 'A' and target == ipv4_address) or (field_type == 'AAAA' and target == ipv6_address):
                self.logger.info('Deleting domain (%s) %s, id: %s', field_type, domain_name, domain_id)
                self.client.delete(f'/domain/zone/{self.zone_name}/record/{domain_id}')

    def __cache_all_domains(self):
        """ Fetch all domains"""
        response = self.client.get(f'/domain/zone/{self.zone_name}/record')

        self.domains = {}

        for domain_id in response:
            domain = self.client.get(f'/domain/zone/{self.zone_name}/record/{domain_id}')
            field_type = domain['fieldType']
            sub_domain = domain['subDomain']
            target = domain['target']
            domain_id = domain['id']

            if sub_domain not in self.domains:
                self.domains[sub_domain] = []

            self.domains[sub_domain].append({
                'fieldType': f'{field_type}',
                'target': target,
                'domainId': domain_id
            })

        for domain in self.domains:
            sorted(self.domains[domain], key=lambda o: o['fieldType'])
