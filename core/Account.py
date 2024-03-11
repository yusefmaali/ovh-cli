import logging

import ovh


class Account:
    client: ovh.Client

    def __init__(self):
        self.logger = logging.getLogger("Account")
        self.client = ovh.Client()

    def register_consumer_key(self):
        ck = self.client.new_consumer_key_request()
        ck.add_recursive_rules(ovh.API_READ_WRITE, '/')  # FIXME

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
