from nodewatcher.core.generator.cgm import base as cgm_base

# These must be the same as defined in package 'identity-pubkey'.
IDENTITY_CERTIFICATE_LOCATION = '/etc/crypto/certificate/identity'
IDENTITY_KEY_LOCATION = '/etc/crypto/private_key/identity'


@cgm_base.register_platform_module('openwrt', 900)
def public_key_identity(node, cfg):
    """
    Configures public key identity on a node.
    """

    # Configure uhttpd so it will serve files via TLS.
    uhttpd = cfg.uhttpd.find_named_section('uhttpd')
    if uhttpd and uhttpd.listen_http:
        router_id = node.config.core.routerid(queryset=True).get(rid_family='ipv4').router_id
        uhttpd.listen_https = ['%s:443' % router_id]
        uhttpd.cert = IDENTITY_CERTIFICATE_LOCATION
        uhttpd.key = IDENTITY_KEY_LOCATION

    # Configure nodewatcher-agent so it will use the generated keys for authentication
    # when configured for push.
    agent = cfg.nodewatcher.find_ordered_section('agent')
    if agent and agent.push_server_pubkey:
        agent.push_client_certificate = IDENTITY_CERTIFICATE_LOCATION
        agent.push_client_key = IDENTITY_KEY_LOCATION

    cfg.packages.update([
        'uhttpd-mod-tls',
        # Require the identity-pubkey package which will generate the node's key pair on first boot.
        'identity-pubkey',
    ])
