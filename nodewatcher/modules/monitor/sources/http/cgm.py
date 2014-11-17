from django.utils.translation import ugettext as _

from nodewatcher.core import models as core_models
from nodewatcher.core.generator.cgm import base as cgm_base


@cgm_base.register_platform_module('openwrt', 50)
def general(node, cfg):
    """
    Register packages needed for reporting via HTTP.
    """

    # Configure the uhttpd server
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

    cfg.packages.update([
        'uhttpd',
        'nodewatcher-agent',
        'nodewatcher-agent-mod-general',
    ])
