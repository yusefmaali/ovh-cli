import logging

import ovh


class Account:
    logger: logging.Logger
    client: ovh.Client

    def __init__(self):
        self.logger = logging.getLogger("Account")
        self.client = ovh.Client()

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
        self.logger.info("Welcome %s", self.client.get('/me')['firstname'])
