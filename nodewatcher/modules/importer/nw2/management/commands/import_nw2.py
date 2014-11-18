# coding: utf-8
import datetime
import json
import pytz

from django.apps import apps
from django.core.management import base
from django.contrib.auth import models as auth_models
from django.db import transaction

from guardian import shortcuts

from nodewatcher.core import models as core_models
from nodewatcher.core.allocation.ip import models as pool_models
from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.monitor import models as monitor_models
from nodewatcher.modules.administration.description import models as dsc_models
from nodewatcher.modules.administration.location import models as location_models
from nodewatcher.modules.administration.projects import models as project_models
from nodewatcher.modules.administration.roles import models as role_models
from nodewatcher.modules.administration.types import models as type_models
from nodewatcher.modules.equipment.antennas import models as antenna_models
from nodewatcher.modules.vpn.tunneldigger import models as tunneldigger_models
from nodewatcher.utils import ipaddr

# Applications that this import process requires to be installed
REQUIRED_APPS = [
    'nodewatcher.core.allocation.ip',
    'nodewatcher.core.generator.cgm',
    'nodewatcher.core.generator',
    'nodewatcher.modules.administration.types',
    'nodewatcher.modules.administration.projects',
    'nodewatcher.modules.administration.location',
    'nodewatcher.modules.administration.description',
    'nodewatcher.modules.administration.roles',
    'nodewatcher.modules.administration.status',
    'nodewatcher.modules.equipment.antennas',
    'nodewatcher.modules.routing.olsr',
    'nodewatcher.modules.sensors.digitemp',
    'nodewatcher.modules.sensors.solar',
    'nodewatcher.modules.vpn.tunneldigger',
]

# Mapping of nodewatcher v2 node types to v3 node types
TYPE_MAP = {
    1: 'server',
    2: 'wireless',
    3: 'test',
    5: 'mobile',
    6: 'dead',
}

# Mapping of nodewatcher v2 device identifiers to v3 device identifiers
ROUTER_MAP = {
    "wrt54g": "wrt54gl",
    "wrt54gl": "wrt54gl",
    "wrt54gs": "wrt54gs",
    "whr-hp-g54": "whr-hp-g54",
    "fonera": "fon-2100",
    "foneraplus": "fon-2200",
    "wl-500gp": "wl500gpv1",
    "wl-500gp-v1": "wl500gpv1",
    "wl-500gd": "wl500gpv1",
    "rb433ah": "rb433ah",
    "tp-wr741nd": "tp-wr741ndv4",
    "tp-wr740nd": "tp-wr740ndv1",
    "tp-wr743nd": "tp-wr743ndv1",
    "tp-wr842nd": "tp-wr842ndv1",
    "tp-mr3020": "tp-mr3020v1",
    "tp-mr3040": "tp-mr3040v1",
    "tp-wr841nd": "tp-wr841ndv3",
    "tp-wr841ndv8": "tp-wr841ndv8",
    "tp-wr703n": "tp-wr703nv1",
    "ub-bullet": "ub-bullet",
    "ub-nano": "ub-nano",
    "ub-bullet-m5": "ub-bullet-m5",
    "ub-rocket-m5": "ub-rocket-m5",
    "tp-wr941nd": "tp-wr941ndv4",
    "tp-wr1041nd": "tp-wr1041ndv2",
    "tp-wr1043nd": "tp-wr1043ndv1",
    "sm-sx763v2": "sm-sx763v2",
    "tp-wdr4300": "tp-wdr4300v1",
}

# Mapping of v2 device identifiers to v3 wireless protocol identifiers
WIFI_PROTOCOL_MAP = {
    "wrt54g": "ieee-80211bg",
    "wrt54gl": "ieee-80211bg",
    "wrt54gs": "ieee-80211bg",
    "whr-hp-g54": "ieee-80211bg",
    "fonera": "ieee-80211bg",
    "foneraplus": "ieee-80211bg",
    "wl-500gp": "ieee-80211bg",
    "wl-500gp-v1": "ieee-80211bg",
    "wl-500gd": "ieee-80211bg",
    "rb433ah": "ieee-80211bg",
    "tp-wr741nd": "ieee-80211bgn",
    "tp-wr740nd": "ieee-80211bgn",
    "tp-wr743nd": "ieee-80211bgn",
    "tp-wr842nd": "ieee-80211bgn",
    "tp-mr3020": "ieee-80211bgn",
    "tp-mr3040": "ieee-80211bgn",
    "tp-wr841nd": "ieee-80211bgn",
    "tp-wr841ndv8": "ieee-80211bgn",
    "tp-wr703n": "ieee-80211bgn",
    "tp-wr941nd": "ieee-80211bgn",
    "tp-wr1041nd": "ieee-80211bgn",
    "tp-wr1043nd": "ieee-80211bgn",
    "ub-bullet": "ieee-80211an",
    "ub-nano": "ieee-80211an",
    "ub-bullet-m5": "ieee-80211an",
    "ub-rocket-m5": "ieee-80211an",
    "sm-sx763v2": "ieee-80211bg",
    "tp-wdr4300": "ieee-80211bgn",
}

# A list of VPN servers as nodewatcher v2 had them hardcoded
VPN_SERVERS = {
    "46.54.226.43": (8942, 53, 123),
    "92.53.140.74": (8942, 53, 123),
}

# A list of DNS servers as nodewatcher v2 had them hardcoded
DNS_SERVERS = {
    "10.254.0.1",
    "10.254.0.2",
}


class Command(base.BaseCommand):
    help = "Imports legacy nodewatcher v2 data."
    requires_model_validation = True

    def handle(self, *args, **options):
        if len(args) != 1:
            raise base.CommandError('Missing filename argument!')

        # Validate that all the required applications are registered
        for app_name in REQUIRED_APPS:
            if not apps.is_installed(app_name):
                raise base.CommandError('Required application \'%s\' is not installed!' % app_name)

        input_filename = args[0]
        try:
            input_file = open(input_filename, 'r')
        except IOError:
            raise base.CommandError("Unable to open file '%s'!" % input_filename)

        self.stdout.write('Loading export file \'%s\'...\n' % input_filename)
        data = json.load(input_file)

        with transaction.atomic():
            self.import_users(data)
            self.import_pools(data)
            self.import_projects(data)
            self.import_nodes(data)

        self.stdout.write('Import completed.\n')

    def get_date(self, date):
        if date is None:
            return None

        try:
            return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f').replace(
                tzinfo=pytz.timezone('Europe/Ljubljana'))
        except ValueError:
            return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S').replace(
                tzinfo=pytz.timezone('Europe/Ljubljana'))

    @transaction.atomic
    def import_users(self, data):
        self.stdout.write('Importing %d users...\n' % len(data['users']))

        for user in data['users'].values():
            # Create user object
            user_mdl = auth_models.User(
                username=user['username'],
                password=user['password'],
                email=user['email'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                is_staff=user['is_staff'],
                is_superuser=user['is_superuser'],
                is_active=True,
                date_joined=self.get_date(user['date_joined']),
            )
            user_mdl.save()
            user['_model'] = user_mdl

            # Create user profile
            profile = user_mdl.profile
            profile.phone_number = user['profile']['phone_number']
            profile.country = user['profile']['country']
            profile.attribution = user['profile']['attribution']
            profile.language = user['profile']['language']
            profile.save()

    def import_pools(self, data):
        self.stdout.write('Importing %d top-level pools...\n' % len(data['pools']))

        for pool in data['pools'].values():
            pool_mdl = pool_models.IpPool(
                family='ipv4',
                network=pool['network'],
                prefix_length=pool['cidr'],
                description=pool['description'],
                prefix_length_default=pool['default_prefix_len'],
                prefix_length_minimum=pool['min_prefix_len'],
                prefix_length_maximum=pool['max_prefix_len'],
            )
            pool_mdl.save()
            pool['_model'] = pool_mdl

    def import_projects(self, data):
        self.stdout.write('Importing %d projects...\n' % len(data['projects']))

        for project in data['projects'].values():
            project_mdl = project_models.Project(
                name=project['name'],
                description=project['description'],
            )
            if project['geo_lat'] and project['geo_long']:
                project_mdl.location = 'POINT(%f %f)' % (project['geo_long'], project['geo_lat'])

            project_mdl.save()
            project['_model'] = project_mdl

            if project['ssid']:
                project_mdl.ssids.create(
                    purpose='ap',
                    default=True,
                    essid=project['ssid'],
                    bssid='02:CA:FF:EE:BA:BE',
                )
            if project['ssid_backbone']:
                project_mdl.ssids.create(
                    purpose='backbone',
                    essid=project['ssid_backbone'],
                )
            if project['ssid_mobile']:
                project_mdl.ssids.create(
                    purpose='mobile',
                    essid=project['ssid_mobile'],
                )

            for pool in project['pools']:
                project_mdl.pools_core_ippool.add(data['pools'][str(pool)]['_model'])

    def import_nodes(self, data):
        self.stdout.write('Importing %d nodes...\n' % len(data['nodes']))

        for idx, node in enumerate(data['nodes'].values()):
            self.stdout.write('  o Importing node %s (%d/%d).\n' % (node['uuid'], idx + 1, len(data['nodes'])))

            # Determine router ID
            try:
                subnet_mesh = [x for x in node['subnets'] if x['gen_iface_type'] == 2][0]
            except IndexError:
                self.stdout.write('  o Skipping node %s (unable to determine router ID).\n' % node['uuid'])
                continue

            subnet_mesh = ipaddr.IPNetwork('%(subnet)s/%(cidr)s' % subnet_mesh)
            try:
                pool_mesh = [x['_model'] for x in data['pools'].values() if subnet_mesh in x['_model']][0]
            except IndexError:
                raise base.CommandError('Failed to find pool instance for subnet \'%s\'!' % subnet_mesh)

            allocation = pool_mesh.reserve_subnet(str(subnet_mesh.ip), subnet_mesh.prefixlen)
            if allocation is None:
                raise base.CommandError('Failed to allocate subnet \'%s\'!' % subnet_mesh)

            node_mdl = core_models.Node(uuid=node['uuid'])
            node_mdl.save()
            node['_model'] = node_mdl

            # Router ID
            node_mdl.config.core.routerid(
                create=pool_models.AllocatedIpRouterIdConfig,
                family='ipv4',
                pool=pool_mesh,
                prefix_length=subnet_mesh.prefixlen,
                allocation=allocation,
            ).save()

            # Assign default permissions
            maintainer = data['users'][str(node['owner_id'])]['_model']
            shortcuts.assign_perm('change_node', maintainer, node_mdl)
            shortcuts.assign_perm('delete_node', maintainer, node_mdl)
            shortcuts.assign_perm('reset_node', maintainer, node_mdl)
            shortcuts.assign_perm('generate_firmware', maintainer, node_mdl)

            # Last seen / first seen
            node_mdl.monitoring.core.general(
                create=monitor_models.GeneralMonitor,
                first_seen=self.get_date(node['first_seen']),
                last_seen=self.get_date(node['last_seen']),
            )

            # Type config
            node_mdl.config.core.type(
                create=type_models.TypeConfig,
                type=TYPE_MAP[node['node_type']],
            )

            # Project config
            node_mdl.config.core.project(
                create=project_models.ProjectConfig,
                project=data['projects'][str(node['project_id'])]['_model'],
            )

            # Location config
            project = node_mdl.config.core.project().project
            if project.name in [u'Števerjan']:
                city = u'Števerjan'
                country = 'IT'
            elif project.name in [u'Maribor', u'Murska Sobota', u'Kranj', u'Sežana', u'Slovenska Bistrica', u'Haloze', u'Vipava']:
                city = project.name
                country = 'SI'
            elif project.name in [u'London']:
                city = project.name
                country = 'GB'
            elif project.name in [u'Croatia']:
                city = ''
                country = 'HR'
            elif project.name in [u'Dolenjska']:
                city = ''
                country = 'SI'
            else:
                city = 'Ljubljana'
                country = 'SI'

            node_mdl.config.core.location(
                create=location_models.LocationConfig,
                address=node['location'] or '',
                city=city,
                country=country,
                timezone='Europe/Ljubljana',
                altitude=0,
                geolocation='POINT(%f %f)' % (node['geo_long'], node['geo_lat']) if node['geo_lat'] else None,
            )

            # Description config
            node_mdl.config.core.description(
                create=dsc_models.DescriptionConfig,
                notes=node['notes'] or '',
                url=node['url'] or ''
            )

            # Role config
            node_mdl.config.core.roles(create=role_models.SystemRoleConfig, system=node['system_node']).save()
            node_mdl.config.core.roles(create=role_models.BorderRouterRoleConfig, border_router=node['border_router']).save()
            node_mdl.config.core.roles(create=role_models.VpnServerRoleConfig, vpn_server=node['vpn_server']).save()
            node_mdl.config.core.roles(create=role_models.RedundantNodeRoleConfig, redundancy_required=node['redundancy_req']).save()

            if node['profile']:
                general = node_mdl.config.core.general(
                    create=cgm_models.CgmGeneralConfig,
                    name=node['name'],
                    platform='openwrt',
                    router=ROUTER_MAP[node['profile']['template']],
                )
                device = general.get_device()

                # Password authentication config
                node_mdl.config.core.authentication(
                    create=cgm_models.PasswordAuthenticationConfig,
                    password=node['profile']['root_pass'],
                ).save()

                # Wireless interface config
                radio_wifi = node_mdl.config.core.interfaces(
                    create=cgm_models.WifiRadioDeviceConfig,
                    wifi_radio='wifi0',
                    protocol=WIFI_PROTOCOL_MAP[node['profile']['template']],
                    channel_width='ht20',
                    channel='ch%d' % node['profile']['channel'],
                    antenna_connector='a1',
                )
                radio_wifi.save()

                # Antenna
                try:
                    node_mdl.config.core.equipment.antenna(
                        create=antenna_models.AntennaEquipmentConfig,
                        device=radio_wifi,
                        antenna=antenna_models.Antenna.objects.get(
                            internal_for=ROUTER_MAP[node['profile']['template']],
                            internal_id='a1'
                        ),
                    ).save()
                except antenna_models.Antenna.DoesNotExist:
                    pass

                # Mesh interface
                ssid = project.ssids.get(default=True)
                iface_mesh = node_mdl.config.core.interfaces(
                    create=cgm_models.WifiInterfaceConfig,
                    device=radio_wifi,
                    mode='mesh',
                    essid=ssid.essid,
                    bssid=ssid.bssid,
                    routing_protocol='olsr',
                )
                iface_mesh.save()

                # WAN uplink
                iface_wan = node_mdl.config.core.interfaces(
                    create=cgm_models.EthernetInterfaceConfig,
                    eth_port='wan0',
                    uplink=True,
                )
                iface_wan.save()

                if node['profile']['wan_dhcp']:
                    node_mdl.config.core.interfaces.network(
                        create=cgm_models.DHCPNetworkConfig,
                        interface=iface_wan,
                        description='WAN',
                    ).save()
                else:
                    node_mdl.config.core.interfaces.network(
                        create=cgm_models.StaticNetworkConfig,
                        interface=iface_wan,
                        description='WAN',
                        family='ipv4',
                        address='%(wan_ip)s/%(wan_cidr)s' % node['profile'],
                        gateway=node['profile']['wan_gw']
                    ).save()

                # LAN subnets
                if device.get_port('lan0'):
                    iface_lan = node_mdl.config.core.interfaces(
                        create=cgm_models.EthernetInterfaceConfig,
                        eth_port='lan0',
                    )
                    iface_lan.save()

                    have_subnets = False
                    for subnet in node['subnets']:
                        if subnet['gen_iface_type'] != 0:
                            continue

                        subnet_lan = ipaddr.IPNetwork('%(subnet)s/%(cidr)s' % subnet)
                        try:
                            pool_lan = [x['_model'] for x in data['pools'].values() if subnet_lan in x['_model']][0]
                        except IndexError:
                            raise base.CommandError('Failed to find pool instance for subnet \'%s\'!' % subnet_lan)

                        allocation = pool_lan.reserve_subnet(str(subnet_lan.ip), subnet_lan.prefixlen)
                        if allocation is None:
                            raise base.CommandError('Failed to allocate subnet \'%s\'!' % subnet_lan)

                        subnet_lan = node_mdl.config.core.interfaces.network(
                            create=cgm_models.AllocatedNetworkConfig,
                            interface=iface_lan,
                            description='LAN',
                            family='ipv4',
                            pool=pool_lan,
                            prefix_length=subnet_lan.prefixlen,
                            allocation=allocation,
                        )
                        subnet_lan.save()
                        have_subnets = True

                    if not have_subnets:
                        # If no subnets are configured, designate the interface for routing
                        iface_lan.routing_protocol = 'olsr'
                        iface_lan.save()

                # VPN
                if node['profile']['use_vpn']:
                    for server, ports in VPN_SERVERS.items():
                        iface_vpn = node_mdl.config.core.interfaces(
                            create=tunneldigger_models.TunneldiggerInterfaceConfig,
                            routing_protocol='olsr',
                        )
                        iface_vpn.save()

                        # Throughput limits
                        if node['profile']['vpn_egress_limit'] or node['profile']['vpn_ingress_limit']:
                            node_mdl.config.core.interfaces.limits(
                                create=cgm_models.ThroughputInterfaceLimitConfig,
                                interface=iface_vpn,
                                limit_in=str(node['profile']['vpn_ingress_limit'] or ''),
                                limit_out=str(node['profile']['vpn_egress_limit'] or ''),
                            ).save()

                        for port in ports:
                            server_vpn = node_mdl.config.core.servers.tunneldigger(
                                create=tunneldigger_models.TunneldiggerServerConfig,
                                tunnel=iface_vpn,
                                address=server,
                                port=port,
                            )
                            server_vpn.save()

                # DNS servers
                for server in DNS_SERVERS:
                    node_mdl.config.core.servers.dns(
                        create=cgm_models.DnsServerConfig,
                        address=server,
                    ).save()

                # Optional packages
                if node['profile']['packages']:
                    # TODO: Implement configuration for packages that were available in v2
                    pass
            else:
                node_mdl.config.core.general(
                    create=core_models.GeneralConfig,
                    name=node['name'],
                )
