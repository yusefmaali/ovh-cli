ovh-cli
=======

An Ovh command line interface to allow easy interaction with the Ovh Api


Usage
-----

Run the ``ovh-cli`` command to see the usage and the available commands.

Currently only a very small sub-set of Ovh's Api are available.


Configuration Quick Steps
-------------------------

1. Create an Ovh application
****************************

Create an Ovh Application to get the ``application_key`` and the ``application_secret`` (`create-an-application <https://github.com/ovh/python-ovh?tab=readme-ov-file#1-create-an-application>`_).

- `OVH Europe <https://eu.api.ovh.com/createApp/>`_
- `OVH US <https://api.us.ovhcloud.com/createApp/>`_
- `OVH North-America <https://ca.api.ovh.com/createApp/>`_
- `So you Start Europe <https://eu.api.soyoustart.com/createApp/>`_
- `So you Start North America <https://ca.api.soyoustart.com/createApp/>`_
- `Kimsufi Europe <https://eu.api.kimsufi.com/createApp/>`_
- `Kimsufi North America <https://ca.api.kimsufi.com/createApp/>`_

2. Create the ``ovh.conf`` file
*******************************

In order to enable ``ovh-cli``, you need to create an ``ovh.conf`` file (`configure-your-application <https://github.com/ovh/python-ovh?tab=readme-ov-file#2-configure-your-application>`_).

.. code:: ini

    [default]
    endpoint=ovh-eu

    [ovh-eu]
    application_key=<value>
    application_secret=<value>
    consumer_key=<value>

Fill the ``endpoint`` param with one of these values:

* ``ovh-eu`` for OVH Europe API
* ``ovh-us`` for OVH US API
* ``ovh-ca`` for OVH North-America API
* ``soyoustart-eu`` for So you Start Europe API
* ``soyoustart-ca`` for So you Start North America API
* ``kimsufi-eu`` for Kimsufi Europe API
* ``kimsufi-ca`` for Kimsufi North America API

Fill the ``application_key`` and the ``application_secret`` params with the values got in the previous step.

The ``consumer_key`` can be fetch in the next step.

3. Authorize the Ovh application and get the ``consumer_key``
*************************************************************

Make sure the ``ovh.conf`` is properly configured with ``endpoint``, ``application_key`` and ``application_secret`` params.

Run

.. code-block:: sh

    ovh-cli account register

and follow the instructions. At the end of the process, you'll get the ``consumer_key``.


Official documentation
----------------------

Enable the access to the Ovh Api: `First Steps with the OVHcloud APIs <https://help.ovhcloud.com/csm/en-gb-api-getting-started-ovhcloud-api?id=kb_article_view&sysparm_article=KB0042784>`_

Ovh Python Api wrapper documentation: `github.com/ovh/python-ovh <https://github.com/ovh/python-ovh>`_


Meta
----

Yusef Maali - contact@yusefmaali.net

Distributed under the MIT license. See `LICENSE.txt <https://github.com/yusefmaali/ovh-cli/blob/master/LICENSE.txt>`_ for more information.

https://github.com/yusefmaali/ovh-cli
