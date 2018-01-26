Python Sahara client
====================

Overview
--------

Sahara Client provides a list of Python interfaces to communicate with the
Sahara REST API. Sahara Client enables users to perform most of the existing
operations like retrieving template lists, creating Clusters, submitting EDP
Jobs, etc.


Instantiating a Client
----------------------

To start using the Sahara Client users have to create an instance of the
`Client` class. The client constructor has a list of parameters to authenticate
and locate Sahara endpoint.

.. autoclass:: saharaclient.api.client.Client
    :members:

**Important!**
 It is not a mandatory rule to provide all of the parameters above. The minimum
 number should be enough to determine Sahara endpoint, check user
 authentication and tenant to operate in.

Authentication check
~~~~~~~~~~~~~~~~~~~~

Passing authentication parameters to Sahara Client is deprecated. Keystone
Session object should be used for this purpose. For example:

.. sourcecode:: python

    from keystoneauth1.identity import v2
    from keystoneauth1 import session
    from saharaclient import client

    auth = v2.Password(auth_url=AUTH_URL,
                       username=USERNAME,
                       password=PASSWORD,
                       tenant_name=PROJECT_ID)

    ses = session.Session(auth=auth)

    sahara = client.Client('1.1', session=ses)
..

For more information about Keystone Sessions, see `Using Sessions`_.

.. _Using Sessions: https://docs.openstack.org/python-keystoneclient/latest/using-sessions.html

Sahara endpoint discovery
~~~~~~~~~~~~~~~~~~~~~~~~~

If user has a direct URL pointing to Sahara REST API, it may be specified as
`sahara_url`. If this parameter is missing, Sahara client will use Keystone
Service Catalog to find the endpoint. There are two parameters: `service_type`
and `endpoint_type` to configure endpoint search. Both parameters have
default values.

.. sourcecode:: python

        from keystoneauth1.identity import v2
        from keystoneauth1 import session
        from saharaclient import client

        auth = v2.Password(auth_url=AUTH_URL,
                           username=USERNAME,
                           password=PASSWORD,
                           tenant_name=PROJECT_ID)

        ses = session.Session(auth=auth)

        sahara = client.Client('1.1', session=ses,
                               service_type="non-default-service-type",
                               endpoint_type="internalURL")
..

Object managers
---------------
Sahara Client has a list of fields to operate with:

 * plugins
 * clusters
 * cluster_templates
 * node_group_templates
 * images
 * data_sources
 * job_binaries
 * job_binary_internals
 * job_executions
 * job_types

Each of this fields is a reference to a Manager for a corresponding group of
REST calls.


Supported operations
--------------------

Plugin ops
~~~~~~~~~~

.. autoclass:: saharaclient.api.plugins.PluginManagerV1
    :members:
    :inherited-members:

Image Registry ops
~~~~~~~~~~~~~~~~~~

.. autoclass:: saharaclient.api.images.ImageManagerV1
    :members:
    :inherited-members:

Node Group Template ops
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: saharaclient.api.node_group_templates.NodeGroupTemplateManagerV1
    :members:
    :inherited-members:

Cluster Template ops
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: saharaclient.api.cluster_templates.ClusterTemplateManagerV1
    :members:
    :inherited-members:

Cluster ops
~~~~~~~~~~~

.. autoclass:: saharaclient.api.clusters.ClusterManagerV1
   :members:
   :inherited-members:

Data Source ops
~~~~~~~~~~~~~~~

.. autoclass:: saharaclient.api.data_sources.DataSourceManagerV1
   :members:
   :inherited-members:

Job Binary Internal ops
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: saharaclient.api.job_binary_internals.JobBinaryInternalsManager
   :members: create, update

Job Binary ops
~~~~~~~~~~~~~~

.. autoclass:: saharaclient.api.job_binaries.JobBinariesManagerV1
   :members:
   :inherited-members:

Job ops
~~~~~~~

.. autoclass:: saharaclient.api.jobs.JobsManagerV1
   :members:
   :inherited-members:

Job Execution ops
~~~~~~~~~~~~~~~~~

.. autoclass:: saharaclient.api.job_executions.JobExecutionsManager
   :members:
   :inherited-members:

Job Types ops
~~~~~~~~~~~~~

.. autoclass:: saharaclient.api.job_types.JobTypesManager
   :members:
   :inherited-members:
