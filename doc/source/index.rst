Python bindings to the OpenStack Sahara API
===========================================

This is a client for OpenStack Sahara API. There's :doc:`a Python API
<api>` (the :mod:`saharaclient` module), and a :doc:`command-line utility
<shell>` (installed as an OpenStackClient plugin). Each implements the entire
OpenStack Sahara API.

You'll need credentials for an OpenStack cloud that implements the
Data Processing API, in order to use the sahara client.

You may want to read the `OpenStack Sahara Docs`__  -- the overview, at
least -- to get an idea of the concepts. By understanding the concepts
this library should make more sense.

 __ http://docs.openstack.org/developer/sahara/

Contents:

.. toctree::
   :maxdepth: 2

   api
   shell
   cli
   how_to_participate

Contributing
============

Code is hosted in `review.o.o`_ and mirrored to `github`_ and `git.o.o`_ .
Submit bugs to the Sahara project on `launchpad`_ and to the Sahara client on
`launchpad_client`_. Submit code to the openstack/python-saharaclient project
using `gerrit`_.

.. _review.o.o: https://review.openstack.org
.. _github: https://github.com/openstack/python-saharaclient
.. _git.o.o: http://git.openstack.org/cgit/openstack/python-saharaclient
.. _launchpad: https://launchpad.net/sahara
.. _launchpad_client: https://launchpad.net/python-saharaclient
.. _gerrit: http://docs.openstack.org/infra/manual/developers.html#development-workflow

