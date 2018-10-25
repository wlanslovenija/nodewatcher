from django import dispatch
from django.apps import apps
from django.utils.translation import ugettext as _

from nodewatcher.core.generator.cgm import base as cgm_base

from . import models


@cgm_base.register_platform_package('openwrt', 'snmpd', models.SNMPDaemonConfig)
def snmp_daemon(node, pkgcfg, cfg):
    """
    Configures SNMP daemon.
    """

    try:
        pkgcfg = pkgcfg.get()
    except cgm_models.SNMPDaemonConfig.MultipleObjectsReturned:
        raise cgm_base.ValidationError(_("Only one SNMP daemon instance can be configured."))

    # Configure SNMP daemon.

    agent = cfg.snmpd.add('agent')
    agent.agentaddress = 'UDP:161'

    agentx = cfg.snmpd.add('agentx')
    agentx.agentxsocket = '/var/run/agentx.sock'
    # Use node name as sysName.
    name = node.config.core.general().name

    system = cfg.snmpd.add('system')
    system.sysName = name
    system.sysLocation = pkgcfg.location
    system.sysContact = pkgcfg.contact
    system.sysObjectID = node.uuid

    public = cfg.snmpd.add(com2sec='public')
    public.source = 'default'
    public.community = pkgcfg.community

    filedescriptors = cfg.snmpd.add(**{'exec': 'filedescriptors'})
    filedescriptors.name = 'filedescriptors'
    filedescriptors.prog = '/bin/cat'
    filedescriptors.args = '/proc/sys/fs/file-nr'

    # Ensure that "snmpd" package is installed.
    cfg.packages.update(['snmpd'])
