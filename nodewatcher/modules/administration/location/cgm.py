from nodewatcher.core.generator.cgm import base as cgm_base


@cgm_base.register_platform_module('openwrt', 900)
def wireless_radio_country(node, cfg):
    """
    Configures country for wireless radios based on the node's location.
    """

    country = node.config.core.location().country
    if not country:
        return

    for radio in cfg.wireless.find_all_named_sections('wifi-device'):
        # If country has already been set by some other module, skip this radio.
        if radio.country:
            continue

        radio.country = str(country)
