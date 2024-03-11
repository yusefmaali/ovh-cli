import logging

import ovh
from ovh import ConsumerKeyRequest


class ZoneManager:
    _logger: logging.Logger
    _client: ovh.Client
    _zone_name: str
    _domains: dict

    @classmethod
    def register_endpoints(cls, ck: ConsumerKeyRequest) -> None:
        ck.add_rules(['GET', 'POST'], '/domain/zone/*/record')
        ck.add_rules(['GET', 'DELETE'], '/domain/zone/*/record/*')
        ck.add_rule('POST', '/domain/zone/*/refresh')

    def __init__(self, zone_name: str, config_file: str = None) -> None:
        self._logger = logging.getLogger("ZoneManager")
        self._client = ovh.Client(config_file=config_file)
        self._zone_name = zone_name
        self._domains = {}

        self._cache_all_domains()

    def domain_exists(self, domain_name: str) -> bool:
        """ Check if a domain exists in the zone """
        return domain_name in self._domains

    def get_hostname_ips(self, host_name: str) -> tuple:
        """ Get the ip addresses of the hostname """
        ipv4_address = None
        ipv6_address = None

        records = self._domains.get(host_name)
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

    def dump_all_domains(self) -> None:
        """ Dump all domains"""
        keys = list(self._domains.keys())

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
            super_groups[key][key] = self._domains.get(key)

            keys.remove(api_key)
            super_groups[key][api_key] = self._domains.get(api_key)

        super_group_keys = list(super_groups.keys())
        super_group_keys.sort()

        self._logger.info('Grouped domains (%d items)', len(super_group_keys))
        for domain in super_group_keys:
            self._logger.info(str(domain).upper())
            for sub_domain in super_groups[domain]:
                self._logger.info('   %s', sub_domain)
                for entry in super_groups[domain][sub_domain]:
                    field_type = entry['fieldType']
                    target = entry['target']
                    self._logger.info('      %s => %s', field_type, target)
            self._logger.info('')

        self._logger.info('')
        self._logger.info('Other domains')
        for domain in keys:
            if len(domain) == 0:
                self._logger.info("(empty)")
            else:
                self._logger.info(domain)

            for entry in self._domains[domain]:
                field_type = entry['fieldType']
                target = entry['target']
                self._logger.info('      %s => %s', field_type, target)

            self._logger.info('')

    def add_domain(self, domain_name: str, ipv4_address: str, ipv6_address: str, add_api_domain: bool) -> None:
        """ Add a test domain
        :param domain_name
        :param ipv4_address
        :param ipv6_address
        :param add_api_domain:
        """
        self._add_domain_action(domain_name, ipv4_address, ipv6_address)

        if add_api_domain:
            api_domain_name = f'api.{domain_name}'
            self._add_domain_action(api_domain_name, ipv4_address, ipv6_address)

        self._client.post(f'/domain/zone/{self._zone_name}/refresh')

    def _add_domain_action(self, domain_name: str, ipv4_address: str, ipv6_address: str) -> None:
        """ Call the action to add a domain.
         Internal method
        :param domain_name
        :param ipv4_address
        :param ipv6_address
        """
        if self.domain_exists(domain_name):
            return

        if ipv4_address is not None:
            self._logger.info('Adding domain (A) %s => %s', domain_name, ipv4_address)
            self._client.post(f'/domain/zone/{self._zone_name}/record',
                              fieldType='A', subDomain=domain_name, target=ipv4_address)

        if ipv6_address is not None:
            self._logger.info('Adding domain (AAAA) %s => %s', domain_name, ipv6_address)
            self._client.post(f'/domain/zone/{self._zone_name}/record',
                              fieldType='AAAA', subDomain=domain_name, target=ipv6_address)

    def delete_domain(self, domain_name: str, ipv4_address: str, ipv6_address: str, delete_api_domain: bool) -> None:
        """ Delete a domain
        :param domain_name
        :param ipv4_address
        :param ipv6_address
        :param delete_api_domain:
        """
        self._delete_domain_action(domain_name, ipv4_address, ipv6_address)

        if delete_api_domain:
            api_domain_name = f'api.{domain_name}'
            self._delete_domain_action(api_domain_name, ipv4_address, ipv6_address)

        self._client.post(f'/domain/zone/{self._zone_name}/refresh')

    def _delete_domain_action(self, domain_name: str, ipv4_address: str, ipv6_address: str) -> None:
        """ Call the action to delete a domain.
         Internal method
        :param domain_name
        :param ipv4_address
        :param ipv6_address
        """
        records = self._domains.get(domain_name)
        if records is None:
            return

        for record in records:
            field_type = record['fieldType']
            target = record['target']
            domain_id = record['domainId']
            if (field_type == 'A' and target == ipv4_address) or (field_type == 'AAAA' and target == ipv6_address):
                self._logger.info('Deleting domain (%s) %s, id: %s', field_type, domain_name, domain_id)
                self._client.delete(f'/domain/zone/{self._zone_name}/record/{domain_id}')

    def _cache_all_domains(self) -> None:
        """ Fetch all domains"""
        response = self._client.get(f'/domain/zone/{self._zone_name}/record')

        self._domains = {}

        for domain_id in response:
            domain = self._client.get(f'/domain/zone/{self._zone_name}/record/{domain_id}')
            field_type = domain['fieldType']
            sub_domain = domain['subDomain']
            target = domain['target']
            domain_id = domain['id']

            if sub_domain not in self._domains:
                self._domains[sub_domain] = []

            self._domains[sub_domain].append({
                'fieldType': f'{field_type}',
                'target': target,
                'domainId': domain_id
            })

        for domain in self._domains:
            self._domains[domain].sort(key=lambda o: o['fieldType'])
