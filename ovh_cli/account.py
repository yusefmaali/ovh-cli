import logging

import ovh
from ovh import ConsumerKeyRequest


class Account:
    _logger: logging.Logger
    _client: ovh.Client
    _consumer_key_request: ConsumerKeyRequest | None

    def __init__(self):
        self._logger = logging.getLogger("Account")
        self._client = ovh.Client()
        self._consumer_key_request = None

    @classmethod
    def register_endpoints(cls, ckr: ConsumerKeyRequest) -> None:
        ckr.add_rule('GET', '/me')

        # Request token
        validation = ck.request()
        validation_url = validation['validationUrl']

        print(f"Please visit {validation_url} to authenticate")
        input("Press Enter to continue...")

        self.greetings()

        consumer_key = validation['consumerKey']
        print(f"Keep note of the consumerKey is '{consumer_key}'")

    def greetings(self):
        """ Log a greeting message """
        self._logger.info("Welcome %s", self._client.get('/me')['firstname'])
