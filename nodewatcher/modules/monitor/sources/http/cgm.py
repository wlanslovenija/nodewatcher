import urlparse

from django.core import urlresolvers
from django.conf import settings
from django.utils.translation import ugettext as _

from nodewatcher.core import models as core_models
from nodewatcher.core.generator.cgm import base as cgm_base


@cgm_base.register_platform_module('openwrt', 50)
def general(node, cfg):
    """
    Register packages needed for reporting via HTTP.
    """

    # Configure the uhttpd server.
    uhttpd = cfg.uhttpd.add(uhttpd='main')
    uhttpd.listen_http = []
    uhttpd.home = '/www'
    uhttpd.cgi_prefix = '/cgi-bin'

    uhttpd.script_timeout = 60
    uhttpd.network_timeout = 30
    uhttpd.tcp_keepalive = 1
    uhttpd.no_dirlists = 1

    try:
        router_id = node.config.core.routerid(queryset=True).get(rid_family='ipv4').router_id
        uhttpd.listen_http.append('%s:80' % router_id)
    except core_models.RouterIdConfig.DoesNotExist:
        raise cgm_base.ValidationError(
            _("In order to use nodewatcher monitoring, the node must have a configured primary IP address.")
        )

    # Configure the nodewatcher agent.
    agent = cfg.nodewatcher.add('agent')
    agent.output_json = '/www/nodewatcher/feed'

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

    cfg.packages.update([
        'uhttpd',
        'nodewatcher-agent',
        'nodewatcher-agent-mod-general',
    ])
