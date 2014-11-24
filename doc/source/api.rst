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

**Important!**
 It is not a mandatory rule to provide all of the parameters above. The minimum number should be enough
 to determine Sahara endpoint, check user authentication and tenant to operate in.

Authentication check
~~~~~~~~~~~~~~~~~~~~

If a user already has a Keystone authentication token, it may be used in `input_auth_token` parameter.

.. sourcecode:: python

    from saharaclient.api.client import Client as saharaclient

    sahara = saharaclient(sahara_url="http://sahara:8386/v1.1",
                          project_id="11111111-2222-3333-4444-555555555555",
                          input_auth_token="66666666-7777-8888-9999-000000000000")
..

In this case no other authentication parameters are required and `input_auth_token` has a higher
priority than other parameters. Otherwise user has to provide:

 * auth_url
 * username
 * api_key
 * any of project_name or project_id

.. sourcecode:: python

    from saharaclient.api.client import Client as saharaclient

    sahara = saharaclient(auth_url="http://keystone:5000/v2.0",
                          sahara_url="http://sahara:8386/v1.1",
                          username="user",
                          api_key="PaSsWoRd",
                          project_name="demo-project")
..


Sahara endpoint discovery
~~~~~~~~~~~~~~~~~~~~~~~~~

If user has a direct URL pointing to Sahara REST API, it may be specified as `sahara_url`.
If this parameter is missing, Sahara client will use Keystone Service Catalog to find the endpoint.
There are two parameters: `service_type` and `endpoint_type` to configure endpoint search. Both parameters have
default values.

.. sourcecode:: python

    from saharaclient.api.client import Client as saharaclient

    sahara = saharaclient(auth_url="http://keystone:5000/v2.0",
                          username="user",
                          api_key="PaSsWoRd",
                          project_name="demo-project",
                          service_type="non-default-service-type",
                          endpoint_type="internalURL")
..


Tenant specification
~~~~~~~~~~~~~~~~~~~~

All Sahara operations should be performed in one of OpenStack tenants.
There are two parameters: `project_name` and `project_id` which allow to specify a tenant.
`project_id` parameter has a higher priority.

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

 * create(name, plugin_name, hadoop_version, flavor_id, description, volumes_per_node, volumes_size, node_processes, node_configs, floating_ip_pool, availability_zone, volumes_availability_zone) - Create a Node Group Template with specified parameters.

Cluster Template ops
~~~~~~~~~~~~~~~~~~~~

 * create(name, plugin_name, hadoop_version, description, cluster_configs, node_groups, anti_affinity, net_id) - Create a Cluster Template with specified parameters.

Cluster ops
~~~~~~~~~~~

 * create(name, plugin_name, hadoop_version, cluster_template_id, default_image_id, is_transient, description, cluster_configs, node_groups, user_keypair_id, anti_affinity, net_id) - Launch a Cluster with specified parameters.
 * scale(cluster_id, scale_object) - Scale an existing Cluster. `scale_object` format is described in REST API doc.

Data Source ops
~~~~~~~~~~~~~~~

 * create(name, description, data_source_type, url, credential_user, credential_pass) - Create a Data Source with specified parameters.

Job Binary Internal ops
~~~~~~~~~~~~~~~~~~~~~~~

 * create(name, data) - Create a Job Binary Internal from provided `data`.

Job Binary ops
~~~~~~~~~~~~~~

 * create(name, url, description, extra) - Create a Job Binary with specified parameters.
 * get_file(job_binary_id) - Download a Job Binary

Job ops
~~~~~~~

 * create(name, type, mains, libs, description) - Create a Job with specified parameters.
 * get_configs(job_type) - Get config hints for a specified Job type.

Job Execution ops
~~~~~~~~~~~~~~~~~

 * create(job_id, cluster_id, input_id, output_id, configs) - Launch a Job with specified parameters.
