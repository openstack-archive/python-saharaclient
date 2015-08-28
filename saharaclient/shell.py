# Copyright 2010 Jacob Kaplan-Moss
# Copyright 2011 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

###
# This code is taken from python-novaclient. Goal is minimal modification.
###

"""
Command-line interface to the OpenStack Sahara API.
"""

from __future__ import print_function
import argparse
import getpass
import logging
import sys

import six


HAS_KEYRING = False
all_errors = ValueError
try:
    import keyring
    HAS_KEYRING = True
    try:
        if isinstance(keyring.get_keyring(), keyring.backend.GnomeKeyring):
            import gnomekeyring
            all_errors = (ValueError,
                          gnomekeyring.IOError,
                          gnomekeyring.NoKeyringDaemonError)
    except Exception:
        pass
except ImportError:
    pass

from keystoneclient.auth.identity.generic import password
from keystoneclient.auth.identity.generic import token
from keystoneclient.auth.identity import v3 as identity
from keystoneclient import session
from oslo_utils import encodeutils
from oslo_utils import strutils

from saharaclient.api import client
from saharaclient.api import shell as shell_api
from saharaclient.openstack.common.apiclient import auth
from saharaclient.openstack.common.apiclient import exceptions as exc
from saharaclient.openstack.common import cliutils
from saharaclient import version

DEFAULT_API_VERSION = 'api'
DEFAULT_ENDPOINT_TYPE = 'publicURL'
DEFAULT_SERVICE_TYPE = 'data-processing'

logger = logging.getLogger(__name__)


def positive_non_zero_float(text):
    if text is None:
        return None
    try:
        value = float(text)
    except ValueError:
        msg = "%s must be a float" % text
        raise argparse.ArgumentTypeError(msg)
    if value <= 0:
        msg = "%s must be greater than 0" % text
        raise argparse.ArgumentTypeError(msg)
    return value


class SecretsHelper(object):
    def __init__(self, args, client):
        self.args = args
        self.client = client
        self.key = None

    def _validate_string(self, text):
        if text is None or len(text) == 0:
            return False
        return True

    def _make_key(self):
        if self.key is not None:
            return self.key
        keys = [
            self.client.auth_url,
            self.client.projectid,
            self.client.user,
            self.client.region_name,
            self.client.endpoint_type,
            self.client.service_type,
            self.client.service_name,
            self.client.volume_service_name,
        ]
        for (index, key) in enumerate(keys):
            if key is None:
                keys[index] = '?'
            else:
                keys[index] = str(keys[index])
        self.key = "/".join(keys)
        return self.key

    def _prompt_password(self, verify=True):
        pw = None
        if hasattr(sys.stdin, 'isatty') and sys.stdin.isatty():
            # Check for Ctl-D
            try:
                while True:
                    pw1 = getpass.getpass('OS Password: ')
                    if verify:
                        pw2 = getpass.getpass('Please verify: ')
                    else:
                        pw2 = pw1
                    if pw1 == pw2 and self._validate_string(pw1):
                        pw = pw1
                        break
            except EOFError:
                pass
        return pw

    def save(self, auth_token, management_url, tenant_id):
        if not HAS_KEYRING or not self.args.os_cache:
            return
        if (auth_token == self.auth_token and
           management_url == self.management_url):
            # Nothing changed....
            return
        if not all([management_url, auth_token, tenant_id]):
            raise ValueError("Unable to save empty management url/auth token")
        value = "|".join([str(auth_token),
                          str(management_url),
                          str(tenant_id)])
        keyring.set_password("saharaclient_auth", self._make_key(), value)

    @property
    def password(self):
        if self._validate_string(self.args.os_password):
            return self.args.os_password
        verify_pass = (
            strutils.bool_from_string(cliutils.env("OS_VERIFY_PASSWORD"))
        )
        return self._prompt_password(verify_pass)

    @property
    def management_url(self):
        if not HAS_KEYRING or not self.args.os_cache:
            return None
        management_url = None
        try:
            block = keyring.get_password('saharaclient_auth',
                                         self._make_key())
            if block:
                _token, management_url, _tenant_id = block.split('|', 2)
        except all_errors:
            pass
        return management_url

    @property
    def auth_token(self):
        # Now is where it gets complicated since we
        # want to look into the keyring module, if it
        # exists and see if anything was provided in that
        # file that we can use.
        if not HAS_KEYRING or not self.args.os_cache:
            return None
        token = None
        try:
            block = keyring.get_password('saharaclient_auth',
                                         self._make_key())
            if block:
                token, _management_url, _tenant_id = block.split('|', 2)
        except all_errors:
            pass
        return token

    @property
    def tenant_id(self):
        if not HAS_KEYRING or not self.args.os_cache:
            return None
        tenant_id = None
        try:
            block = keyring.get_password('saharaclient_auth',
                                         self._make_key())
            if block:
                _token, _management_url, tenant_id = block.split('|', 2)
        except all_errors:
            pass
        return tenant_id


class SaharaClientArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super(SaharaClientArgumentParser, self).__init__(*args, **kwargs)

    def error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.
        """
        self.print_usage(sys.stderr)
        # FIXME(lzyeval): if changes occur in argparse.ArgParser._check_value
        choose_from = ' (choose from'
        progparts = self.prog.partition(' ')
        self.exit(2, "error: %(errmsg)s\nTry '%(mainp)s help %(subp)s'"
                     " for more information.\n" %
                     {'errmsg': message.split(choose_from)[0],
                      'mainp': progparts[0],
                      'subp': progparts[2]})


class OpenStackSaharaShell(object):

    def get_base_parser(self):
        parser = SaharaClientArgumentParser(
            prog='sahara',
            description=__doc__.strip(),
            epilog='See "sahara help COMMAND" '
                   'for help on a specific command.',
            add_help=False,
            formatter_class=OpenStackHelpFormatter,
        )

        # Global arguments
        parser.add_argument('-h', '--help',
                            action='store_true',
                            help=argparse.SUPPRESS)

        parser.add_argument('--version',
                            action='version',
                            version=version.version_info.version_string())

        parser.add_argument('--debug',
                            default=False,
                            action='store_true',
                            help="Print debugging output.")

        parser.add_argument('--os-cache',
                            default=strutils.bool_from_string(
                                cliutils.env('OS_CACHE', default=False)),
                            action='store_true',
                            help="Use the auth token cache. Defaults to False "
                            "if env[OS_CACHE] is not set.")


# TODO(mattf) - add get_timings support to Client
#        parser.add_argument('--timings',
#            default=False,
#            action='store_true',
#            help="Print call timing info")

# TODO(mattf) - use timeout
#        parser.add_argument('--timeout',
#            default=600,
#            metavar='<seconds>',
#            type=positive_non_zero_float,
#            help="Set HTTP call timeout (in seconds)")

        parser.add_argument('--region-name',
                            metavar='<region-name>',
                            default=cliutils.env('SAHARA_REGION_NAME',
                                                 'OS_REGION_NAME'),
                            help='Defaults to env[OS_REGION_NAME].')
        parser.add_argument('--region_name',
                            help=argparse.SUPPRESS)

        parser.add_argument('--service-type',
                            metavar='<service-type>',
                            help='Defaults to data-processing for all '
                                 'actions.')
        parser.add_argument('--service_type',
                            help=argparse.SUPPRESS)

# NA
#        parser.add_argument('--service-name',
#            metavar='<service-name>',
#            default=utils.env('SAHARA_SERVICE_NAME'),
#            help='Defaults to env[SAHARA_SERVICE_NAME]')
#        parser.add_argument('--service_name',
#            help=argparse.SUPPRESS)

# NA
#        parser.add_argument('--volume-service-name',
#            metavar='<volume-service-name>',
#            default=utils.env('NOVA_VOLUME_SERVICE_NAME'),
#            help='Defaults to env[NOVA_VOLUME_SERVICE_NAME]')
#        parser.add_argument('--volume_service_name',
#            help=argparse.SUPPRESS)

        parser.add_argument('--endpoint-type',
                            metavar='<endpoint-type>',
                            default=cliutils.env(
                                'SAHARA_ENDPOINT_TYPE',
                                'OS_ENDPOINT_TYPE',
                                default=DEFAULT_ENDPOINT_TYPE),
                            help=('Defaults to env[SAHARA_ENDPOINT_TYPE] or'
                                  ' env[OS_ENDPOINT_TYPE] or ')
                            + DEFAULT_ENDPOINT_TYPE + '.')
        # NOTE(dtroyer): We can't add --endpoint_type here due to argparse
        #                thinking usage-list --end is ambiguous; but it
        #                works fine with only --endpoint-type present
        #                Go figure.  I'm leaving this here for doc purposes.
        # parser.add_argument('--endpoint_type',
        #    help=argparse.SUPPRESS)

        parser.add_argument('--sahara-api-version',
                            metavar='<sahara-api-ver>',
                            default=cliutils.env(
                                'SAHARA_API_VERSION',
                                default=DEFAULT_API_VERSION),
                            help='Accepts "api", '
                                 'defaults to env[SAHARA_API_VERSION].')
        parser.add_argument('--sahara_api_version',
                            help=argparse.SUPPRESS)

        parser.add_argument('--bypass-url',
                            metavar='<bypass-url>',
                            default=cliutils.env('BYPASS_URL', default=None),
                            dest='bypass_url',
                            help="Use this API endpoint instead of the "
                            "Service Catalog.")
        parser.add_argument('--bypass_url',
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-tenant-name',
                            default=cliutils.env('OS_TENANT_NAME'),
                            help='Defaults to env[OS_TENANT_NAME].')

        parser.add_argument('--os-tenant-id',
                            default=cliutils.env('OS_TENANT_ID'),
                            help='Defaults to env[OS_TENANT_ID].')

        parser.add_argument('--os-auth-system',
                            default=cliutils.env('OS_AUTH_SYSTEM'),
                            help='Defaults to env[OS_AUTH_SYSTEM].')

        parser.add_argument('--os-auth-token',
                            default=cliutils.env('OS_AUTH_TOKEN'),
                            help='Defaults to env[OS_AUTH_TOKEN].')

        # Use Keystoneclient API to parse authentication arguments
        session.Session.register_cli_options(parser)
        identity.Password.register_argparse_arguments(parser)

        return parser

    def get_subcommand_parser(self, version):
        parser = self.get_base_parser()

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')

        try:
            actions_module = {
                'api': shell_api,
            }[version]
        except KeyError:
            actions_module = shell_api
        actions_module = shell_api

        self._find_actions(subparsers, actions_module)
        self._find_actions(subparsers, self)

        self._add_bash_completion_subparser(subparsers)

        return parser

    def _add_bash_completion_subparser(self, subparsers):
        subparser = (
            subparsers.add_parser('bash_completion',
                                  add_help=False,
                                  formatter_class=OpenStackHelpFormatter)
        )
        self.subcommands['bash_completion'] = subparser
        subparser.set_defaults(func=self.do_bash_completion)

    def _find_actions(self, subparsers, actions_module):
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            # I prefer to be hyphen-separated instead of underscores.
            command = attr[3:].replace('_', '-')
            callback = getattr(actions_module, attr)
            desc = callback.__doc__ or ''
            action_help = desc.strip()
            arguments = getattr(callback, 'arguments', [])

            subparser = (
                subparsers.add_parser(command,
                                      help=action_help,
                                      description=desc,
                                      add_help=False,
                                      formatter_class=OpenStackHelpFormatter)
            )
            subparser.add_argument('-h', '--help',
                                   action='help',
                                   help=argparse.SUPPRESS,)
            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    def setup_debugging(self, debug):
        if not debug:
            return

        streamformat = "%(levelname)s (%(module)s:%(lineno)d) %(message)s"
        # Set up the root logger to debug so that the submodules can
        # print debug messages
        logging.basicConfig(level=logging.DEBUG,
                            format=streamformat)

    def _get_keystone_auth(self, session, auth_url, **kwargs):
        auth_token = kwargs.pop('auth_token', None)
        if auth_token:
            return token.Token(auth_url, auth_token, **kwargs)
        else:
            return password.Password(
                auth_url,
                username=kwargs.pop('username'),
                user_id=kwargs.pop('user_id'),
                password=kwargs.pop('password'),
                user_domain_id=kwargs.pop('user_domain_id'),
                user_domain_name=kwargs.pop('user_domain_name'),
                **kwargs)

    def main(self, argv):

        # Parse args once to find version and debug settings
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)
        self.setup_debugging(options.debug)
        self.options = options

        # NOTE(dtroyer): Hackery to handle --endpoint_type due to argparse
        #                thinking usage-list --end is ambiguous; but it
        #                works fine with only --endpoint-type present
        #                Go figure.
        if '--endpoint_type' in argv:
            spot = argv.index('--endpoint_type')
            argv[spot] = '--endpoint-type'

        subcommand_parser = (
            self.get_subcommand_parser(options.sahara_api_version)
        )
        self.parser = subcommand_parser

        if options.help or not argv:
            subcommand_parser.print_help()
            return 0

        args = subcommand_parser.parse_args(argv)

        # Short-circuit and deal with help right away.
        if args.func == self.do_help:
            self.do_help(args)
            return 0
        elif args.func == self.do_bash_completion:
            self.do_bash_completion(args)
            return 0

#        (os_username, os_tenant_name, os_tenant_id, os_auth_url,
#                os_region_name, os_auth_system, endpoint_type, insecure,
#                service_type, service_name, volume_service_name,
#                bypass_url, os_cache, cacert) = ( #, timeout) = (
#                        args.os_username,
#                        args.os_tenant_name, args.os_tenant_id,
#                        args.os_auth_url,
#                        args.os_region_name,
#                        args.os_auth_system,
#                        args.endpoint_type, args.insecure,
#                        args.service_type,
#                        args.service_name, args.volume_service_name,
#                        args.bypass_url, args.os_cache,
#                        args.os_cacert, args.timeout)
        (os_username, os_tenant_name, os_tenant_id,
         os_auth_url, os_auth_system, endpoint_type,
         service_type, bypass_url, os_cacert, insecure, region_name) = (
            (args.os_username, args.os_tenant_name, args.os_tenant_id,
             args.os_auth_url, args.os_auth_system, args.endpoint_type,
             args.service_type, args.bypass_url, args.os_cacert, args.insecure,
             args.region_name)
        )

        if os_auth_system and os_auth_system != "keystone":
            auth_plugin = auth.load_plugin(os_auth_system)
        else:
            auth_plugin = None

        # Fetched and set later as needed
        os_password = None

        if not endpoint_type:
            endpoint_type = DEFAULT_ENDPOINT_TYPE

        if not service_type:
            service_type = DEFAULT_SERVICE_TYPE
# NA - there is only one service this CLI accesses
#            service_type = utils.get_service_type(args.func) or service_type

        # FIXME(usrleon): Here should be restrict for project id same as
        # for os_username or os_password but for compatibility it is not.
        if not cliutils.isunauthenticated(args.func):
            if auth_plugin:
                auth_plugin.parse_opts(args)

            if not auth_plugin or not auth_plugin.opts:
                if not os_username:
                    raise exc.CommandError("You must provide a username "
                                           "via either --os-username or "
                                           "env[OS_USERNAME]")

            if not os_auth_url:
                if os_auth_system and os_auth_system != 'keystone':
                    os_auth_url = auth_plugin.get_auth_url()

            if not os_auth_url:
                    raise exc.CommandError("You must provide an auth url "
                                           "via either --os-auth-url or "
                                           "env[OS_AUTH_URL] or specify an "
                                           "auth_system which defines a "
                                           "default url with --os-auth-system "
                                           "or env[OS_AUTH_SYSTEM]")

# NA
#        if (options.os_compute_api_version and
#                options.os_compute_api_version != '1.0'):
#            if not os_tenant_name and not os_tenant_id:
#                raise exc.CommandError("You must provide a tenant name "
#                        "or tenant id via --os-tenant-name, "
#                        "--os-tenant-id, env[OS_TENANT_NAME] "
#                        "or env[OS_TENANT_ID]")
#
#            if not os_auth_url:
#                raise exc.CommandError("You must provide an auth url "
#                        "via either --os-auth-url or env[OS_AUTH_URL]")

# NOTE: The Sahara client authenticates when you create it. So instead of
#       creating here and authenticating later, which is what the novaclient
#       does, we just create the client later.

        # Now check for the password/token of which pieces of the
        # identifying keyring key can come from the underlying client
        if not cliutils.isunauthenticated(args.func):
            # NA - Client can't be used with SecretsHelper
            # helper = SecretsHelper(args, self.cs.client)
            if (auth_plugin and auth_plugin.opts and
                    "os_password" not in auth_plugin.opts):
                use_pw = False
            else:
                use_pw = True

#            tenant_id, auth_token, management_url = (helper.tenant_id,
#                                                     helper.auth_token,
#                                                     helper.management_url)
#
#            if tenant_id and auth_token and management_url:
#                self.cs.client.tenant_id = tenant_id
#                self.cs.client.auth_token = auth_token
#                self.cs.client.management_url = management_url
#                # authenticate just sets up some values in this case, no REST
#                # calls
#                self.cs.authenticate()
            if use_pw:
                # Auth using token must have failed or not happened
                # at all, so now switch to password mode and save
                # the token when its gotten... using our keyring
                # saver
                # os_password = helper.password
                os_password = args.os_password
                if not os_password:
                    raise exc.CommandError(
                        'Expecting a password provided via either '
                        '--os-password, env[OS_PASSWORD], or '
                        'prompted response')
#                self.cs.client.password = os_password
#                self.cs.client.keyring_saver = helper

        # V3 stuff
        project_info_provided = (self.options.os_tenant_name or
                                 self.options.os_tenant_id or
                                 (self.options.os_project_name and
                                  (self.options.os_project_domain_name or
                                   self.options.os_project_domain_id)) or
                                 self.options.os_project_id)

        if (not project_info_provided):
            raise exc.CommandError(
                ("You must provide a tenant_name, tenant_id, "
                 "project_id or project_name (with "
                 "project_domain_name or project_domain_id) via "
                 "  --os-tenant-name (env[OS_TENANT_NAME]),"
                 "  --os-tenant-id (env[OS_TENANT_ID]),"
                 "  --os-project-id (env[OS_PROJECT_ID])"
                 "  --os-project-name (env[OS_PROJECT_NAME]),"
                 "  --os-project-domain-id "
                 "(env[OS_PROJECT_DOMAIN_ID])"
                 "  --os-project-domain-name "
                 "(env[OS_PROJECT_DOMAIN_NAME])"))

        if not os_auth_url:
            raise exc.CommandError(
                "You must provide an auth url "
                "via either --os-auth-url or env[OS_AUTH_URL]")

        keystone_session = None
        keystone_auth = None
        if not auth_plugin:
            project_id = args.os_project_id or args.os_tenant_id
            project_name = args.os_project_name or args.os_tenant_name

            keystone_session = (session.Session.
                                load_from_cli_options(args))
            keystone_auth = self._get_keystone_auth(
                keystone_session,
                args.os_auth_url,
                username=args.os_username,
                user_id=args.os_user_id,
                user_domain_id=args.os_user_domain_id,
                user_domain_name=args.os_user_domain_name,
                password=args.os_password,
                auth_token=args.os_auth_token,
                project_id=project_id,
                project_name=project_name,
                project_domain_id=args.os_project_domain_id,
                project_domain_name=args.os_project_domain_name)

        self.cs = client.Client(username=os_username,
                                api_key=os_password,
                                project_id=os_tenant_id,
                                project_name=os_tenant_name,
                                auth_url=os_auth_url,
                                sahara_url=bypass_url,
                                endpoint_type=endpoint_type,
                                session=keystone_session,
                                auth=keystone_auth,
                                cacert=os_cacert,
                                insecure=insecure,
                                service_type=service_type,
                                region_name=region_name)

        args.func(self.cs, args)

# TODO(mattf) - add get_timings support to Client
#        if args.timings:
#            self._dump_timings(self.cs.get_timings())

    def _dump_timings(self, timings):
        class Tyme(object):
            def __init__(self, url, seconds):
                self.url = url
                self.seconds = seconds
        results = [Tyme(url, end - start) for url, start, end in timings]
        total = 0.0
        for tyme in results:
            total += tyme.seconds
        results.append(Tyme("Total", total))
        cliutils.print_list(results, ["url", "seconds"], sortby_index=None)

    def do_bash_completion(self, _args):
        """Prints arguments for bash-completion.

        Prints all of the commands and options to stdout so that the
        sahara.bash_completion script doesn't have to hard code them.
        """
        commands = set()
        options = set()
        for sc_str, sc in self.subcommands.items():
            commands.add(sc_str)
            for option in sc._optionals._option_string_actions.keys():
                options.add(option)

        commands.remove('bash-completion')
        commands.remove('bash_completion')
        print(' '.join(commands | options))

    @cliutils.arg('command', metavar='<subcommand>', nargs='?',
                  help='Display help for <subcommand>.')
    def do_help(self, args):
        """Display help about this program or one of its subcommands."""
        if args.command:
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exc.CommandError("'%s' is not a valid subcommand" %
                                       args.command)
        else:
            self.parser.print_help()


# I'm picky about my shell help.
class OpenStackHelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(OpenStackHelpFormatter, self).start_section(heading)


def main():
    try:
        OpenStackSaharaShell().main(map(encodeutils.safe_decode,
                                        sys.argv[1:]))

    except Exception as e:
        logger.debug(e, exc_info=1)
        print("ERROR: %s" % encodeutils.safe_encode(six.text_type(e)),
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
