Python bindings to the OpenStack Savanna API
============================================

This is a client for OpenStack Savanna API. There's :doc:`a Python API
<api>` (the :mod:`savannaclient` module), and a :doc:`command-line script
<shell>` (installed as :program:`savanna`). Each implements the entire
OpenStack Savanna API.

You'll need credentials for an OpenStack cloud that implements the
Data Processing API, in order to use the savanna client.

You may want to read the `OpenStack Savanna Docs`__  -- the overview, at
least -- to get an idea of the concepts. By understanding the concepts
this library should make more sense.

 __ http://docs.openstack.org/developer/savanna/api/index.html

Contents:

.. toctree::
   :maxdepth: 2

   api

Contributing
============

Code is hosted in `review.o.o`_ and mirrored to `github`_ and `git.o.o`_ .
Submit bugs to the Savanna project on `launchpad`_ and to the Savanna client on
`launchpad_client`_. Submit code to the openstack/python-savannaclient project
using `gerrit`_.

.. _review.o.o: https://review.openstack.org
.. _github: https://github.com/openstack/python-savannaclient
.. _git.o.o: http://git.openstack.org/cgit/openstack/python-savannaclient
.. _launchpad: https://launchpad.net/savanna
.. _launchpad_client: https://launchpad.net/python-savannaclient
.. _gerrit: http://wiki.openstack.org/GerritWorkflow

