Introduction
============

The Sahara shell utility now is part of the OpenStackClient, so all
shell commands take the following form:

.. code-block:: bash

    $ openstack dataprocessing <command> [arguments...]

To get a list of all possible commands you can run:

.. code-block:: bash

    $ openstack help dataprocessing

To get detailed help for the command you can run:

.. code-block:: bash

    $ openstack help dataprocessing <command>

For more information about commands and their parameters you can refer to
:doc:`the Sahara CLI commands <reference>`.

For more information about abilities and features of OpenStackClient CLI you
can refer to `OpenStackClient documentation <https://docs.openstack.org/python-openstackclient/latest/>`_

Configuration
-------------

The CLI is configured via environment variables and command-line options which
are described in https://docs.openstack.org/python-openstackclient/latest/cli/authentication.html.

Authentication using username/password is most commonly used and can be
provided with environment variables:

.. code-block:: bash

   export OS_AUTH_URL=<url-to-openstack-identity>
   export OS_PROJECT_NAME=<project-name>
   export OS_USERNAME=<username>
   export OS_PASSWORD=<password>  # (optional)

or command-line options:

.. code-block:: bash

   --os-auth-url <url>
   --os-project-name <project-name>
   --os-username <username>
   [--os-password <password>]

Additionally :program:`sahara` API url can be configured with parameter:

.. code-block:: bash

    --os-data-processing-url

or with environment variable:

.. code-block:: bash

    export OS_DATA_PROCESSING_URL=<url-to-sahara-API>
