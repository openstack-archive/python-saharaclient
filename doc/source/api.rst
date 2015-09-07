Sahara Client
=============

Overview
--------

Sahara Client provides a list of Python interfaces to communicate with the Sahara REST API.
Sahara Client enables users to perform most of the existing operations like retrieving template lists,
creating Clusters, submitting EDP Jobs, etc.


Instantiating a Client
----------------------

To start using the Sahara Client users have to create an instance of the `Client` class.
The client constructor has a list of parameters to authenticate and locate Sahara endpoint.

 * auth_url - Keystone URL that will be used for authentication.
 * sahara_url - Sahara REST API URL to communicate with.
 * service_type - Sahara service name in Keystone catalog. (Default: data-processing)
 * endpoint_type - Desired Sahara endpoint type. (Default: publicURL)
 * username - Username for Keystone authentication.
 * api_key - Password for Keystone authentication.
 * project_name - Keystone Tenant name.
 * project_id - Keystone Tenant id.
 * input_auth_token - Keystone authorization token.
 * insecure - Allow insecure.
 * auth - Keystone Authentication Plugin object.
 * session - Keystone Session object.

**Important!**
 It is not a mandatory rule to provide all of the parameters above. The minimum number should be enough
 to determine Sahara endpoint, check user authentication and tenant to operate in.

Authentication check
~~~~~~~~~~~~~~~~~~~~

Passing authentication parameters to Sahara Client is deprecated. Keystone
Session object should be used for this purpose. For example:

.. sourcecode:: python

    from keystoneclient.auth.identity import v2
    from keystoneclient import session
    from saharaclient import client

    auth = v2.Password(auth_url=AUTH_URL,
                       username=USERNAME,
                       password=PASSWORD,
                       tenant_name=PROJECT_ID)

    ses = session.Session(auth=auth)

    sahara = client.Client('1.1', session=ses)
..

For more information about Keystone Sessions, see `Using Sessions`_.

.. _Using Sessions: http://docs.openstack.org/developer/python-keystoneclient/using-sessions.html

Sahara endpoint discovery
~~~~~~~~~~~~~~~~~~~~~~~~~

If user has a direct URL pointing to Sahara REST API, it may be specified as `sahara_url`.
If this parameter is missing, Sahara client will use Keystone Service Catalog to find the endpoint.
There are two parameters: `service_type` and `endpoint_type` to configure endpoint search. Both parameters have
default values.

.. sourcecode:: python

        from keystoneclient.auth.identity import v2
        from keystoneclient import session
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

Each of this fields is a reference to a Manager for a corresponding group of REST calls.


Supported operations
--------------------

The following methods are allowed for all Managers:

 * list() - Get a list of all objects of specified type.
 * get(id) - Get an object by id. (In case of plugins, the Plugin name should be provided)
 * delete(id) - Delete an object by id. (Available only for templates and EDP objects)

Plugin Manager ops
~~~~~~~~~~~~~~~~~~

 * get_version_details(plugin_name, hadoop_version) - Get the list of Services and Service Parameters for a specified Plugin and Hadoop Version
 * convert_to_cluster_template(plugin_name, hadoop_version, template_name, filecontent) - This call is used to create Cluster Templates directly, avoiding Cluster Template mechanism.

Image Registry ops
~~~~~~~~~~~~~~~~~~

 * update_image(image_id, user_name, descr) - Create or update an Image in Image Registry.
 * unregister_image(image_id) - Remove an Image from Sahara Image Registry.
 * update_tags(image_id, new_tags) - Updates Image tags. `new_tags` list will replace currently assigned tags.

Node Group Template ops
~~~~~~~~~~~~~~~~~~~~~~~

 * create(name, plugin_name, hadoop_version, flavor_id, description, volumes_per_node, volumes_size, node_processes, node_configs, floating_ip_pool, security_groups, auto_security_group, availability_zone, volumes_availability_zone, volume_type, image_id, is_proxy_gateway, volume_local_to_instance, use_autoconfig, shares, is_public, is_protected) - Create a Node Group Template with specified parameters.
 * update(ng_template_id, name, plugin_name, hadoop_version, flavor_id, description, volumes_per_node, volumes_size, node_processes, node_configs, floating_ip_pool, security_groups, auto_security_group, availability_zone, volumes_availability_zone, volume_type, image_id, is_proxy_gateway, volume_local_to_instance, use_autoconfig, shares, is_public, is_protected) - Update a Node Group Template with specified parameters.

Cluster Template ops
~~~~~~~~~~~~~~~~~~~~

 * create(name, plugin_name, hadoop_version, description, cluster_configs, node_groups, anti_affinity, net_id, default_image_id, use_autoconfig, shares, is_public, is_protected) - Create a Cluster Template with specified parameters.
 * update(cluster_template_id, name, plugin_name, hadoop_version, description, cluster_configs, node_groups, anti_affinity, net_id, default_image_id, use_autoconfig, shares, is_public, is_protected) - Update a Cluster Template with specified parameters.

Cluster ops
~~~~~~~~~~~

 * create(name, plugin_name, hadoop_version, cluster_template_id, default_image_id, is_transient, description, cluster_configs, node_groups, user_keypair_id, anti_affinity, net_id, count, use_autoconfig, shares, is_public, is_protected) - Launch a Cluster with specified parameters.
 * scale(cluster_id, scale_object) - Scale an existing Cluster. `scale_object` format is described in REST API doc.
 * update(cluster_id, name, description, is_public, is_protected) - Update a Cluster with specified parameters.

Data Source ops
~~~~~~~~~~~~~~~

 * create(name, description, data_source_type, url, credential_user, credential_pass, is_public, is_protected) - Create a Data Source with specified parameters.
 * update(data_source_id, update_data) - Update a Data Source with provided `data`.

Job Binary Internal ops
~~~~~~~~~~~~~~~~~~~~~~~

 * create(name, data) - Create a Job Binary Internal from provided `data`.
 * update(job_binary_id, name, is_public, is_protected) - Update a Job Binary Internal with specified parameters

Job Binary ops
~~~~~~~~~~~~~~

 * create(name, url, description, extra, is_public, is_protected) - Create a Job Binary with specified parameters.
 * get_file(job_binary_id) - Download a Job Binary.
 * update(job_binary_id, data) - Update Job Binary with provided `data`.

Job ops
~~~~~~~

 * create(name, type, mains, libs, description, interface, is_public, is_protected) - Create a Job with specified parameters.
 * get_configs(job_type) - Get config hints for a specified Job type.
 * update(job_id, name, description, is_public, is_protected) - Update a Job with specified parameters.

Job Execution ops
~~~~~~~~~~~~~~~~~

 * create(job_id, cluster_id, input_id, output_id, configs, interface, is_public, is_protected) - Launch a Job with specified parameters.
 * update(obj_id, is_public, is_protected) - Update a Job Execution with specified parameters.
