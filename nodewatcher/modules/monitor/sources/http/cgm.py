import urlparse

from django.core import urlresolvers
from django.conf import settings
from django.utils.translation import ugettext as _

from nodewatcher.core.generator.cgm import base as cgm_base


@cgm_base.register_platform_module('openwrt', 50)
def general(node, cfg):
    """
    Register packages needed for reporting via HTTP.
    """

    # Configure the nodewatcher agent.
    agent = cfg.nodewatcher.add('agent')

    try:
        router_id = node.config.core.routerid(queryset=True).filter(rid_family='ipv4')[0].router_id

        # Configure the uhttpd server.
        uhttpd = cfg.uhttpd.add(uhttpd='main')
        uhttpd.listen_http = []
        uhttpd.listen_http.append('{}:80'.format(router_id))
        uhttpd.home = '/www'
        uhttpd.cgi_prefix = '/cgi-bin'

        uhttpd.script_timeout = 60
        uhttpd.network_timeout = 30
        uhttpd.tcp_keepalive = 1
        uhttpd.no_dirlists = 1

        # Configure nodewatcher-agent for output via uhttpd.
        agent.output_json = '/www/nodewatcher/feed'

        cfg.packages.add('uhttpd')
    except IndexError:
        # In case no router id is configured, do not configure uhttpd as the node will probably
        # only use push for monitoring.
        pass

    telemetry_source = node.config.core.telemetry.http()
    if telemetry_source.source == 'push':
        if not getattr(settings, 'MONITOR_HTTP_PUSH_HOST', None):
            raise cgm_base.ValidationError(
                _("HTTP push host must be configured in order to configure push.")
            )

        # Configure secure transport when enabled.
        schema = 'http'
        if getattr(settings, 'HTTPS_PUBLIC_KEY', None):
            schema = 'https'
            # Install server's public key.
            pubkey = cfg.crypto.add_object(
                cgm_base.PlatformCryptoManager.PUBLIC_KEY,
                settings.HTTPS_PUBLIC_KEY,
                'server.nodewatcher',
            )
            # Setup public key pinning.
            agent.push_server_pubkey = pubkey.path()

        # Configure agent for periodic push.
        agent.push_url = urlparse.urlunparse((
            schema,
            settings.MONITOR_HTTP_PUSH_HOST,
            urlresolvers.reverse('HttpPushComponent:endpoint', kwargs={'uuid': str(node.uuid)}),
            None,
            None,
            None,
        ))
        agent.push_interval = 300

        # Ensure that HTTP push module is installed.
        cfg.packages.add('nodewatcher-agent-mod-http_push')

    # We will require nodewatcher-agent in all cases.
    cfg.packages.update([
        'nodewatcher-agent',
        'nodewatcher-agent-mod-general',
    ])
