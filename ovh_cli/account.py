import logging

import ovh
from ovh import ConsumerKeyRequest


class Account:
    _logger: logging.Logger
    _client: ovh.Client
    _consumer_key_request: ConsumerKeyRequest | None

    def __init__(self, config_file: str = None) -> None:
        self._logger = logging.getLogger("Account")
        self._client = ovh.Client(config_file=config_file)
        self._consumer_key_request = None

    @classmethod
    def register_endpoints(cls, ckr: ConsumerKeyRequest) -> None:
        ckr.add_rule('GET', '/me')

    @property
    def consumer_key_request(self) -> ConsumerKeyRequest:
        return self._consumer_key_request

    def consumer_key_create_request(self) -> None:
        self._consumer_key_request = self._client.new_consumer_key_request()

    def consumer_key_complete_registration(self) -> (str, str):
        validation = self.consumer_key_request.request()
        return validation['validationUrl'], validation['consumerKey']

    def greetings(self) -> None:
        """ Log a greeting message """
        self._logger.info("Welcome %s", self._client.get('/me')['firstname'])
