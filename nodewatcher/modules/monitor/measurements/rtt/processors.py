import subprocess
import threading
import collections
import math

from django.conf import settings
from django.utils import timezone

from nodewatcher.core import models as core_models
from nodewatcher.core.monitor import models as monitor_models, processors as monitor_processors
from nodewatcher.utils import which, ipaddr


class RttMeasurement(monitor_processors.NetworkProcessor):
    """
    Performs RTT measurements to nodes using different packet sizes.
    """

    PACKET_SIZES = (56, 100, 500, 1000, 1480)
    PACKET_COUNT = 10

    def process(self, context, nodes):
        """
        Performs network-wide processing and selects the nodes that will be processed
        in any following processors.

        :param context: Current context
        :param nodes: A set of nodes that are to be processed
        :return: A (possibly) modified context and a (possibly) modified set of nodes
        """

        # Detect the location of fping binary
        fping = which.which('fping')
        if not fping:
            self.logger.error("Unable to find 'fping' binary!")
            return context, nodes

        # Check if source node for measurements is configured and valid
        source_node_id = getattr(settings, 'MEASUREMENT_SOURCE_NODE', None)
        try:
            context.rtt.source_node = core_models.Node.objects.get(uuid=source_node_id)
        except core_models.Node.DoesNotExist:
            self.logger.error("Invalid measurement source UUID specified in MEASUREMENT_SOURCE_NODE!")
            return context, nodes

        # Prepare a list of node IPv4 addresses
        node_ips = [
            str(node.config.core.routerid(queryset=True).get(family='ipv4').router_id)
            for node in nodes
        ]

        # Perform ping tests of different sizes
        processes = []
        threads = []
        outputs = collections.deque()
        metadata = collections.deque()
        for size in self.PACKET_SIZES:
            args = [
                fping,
                '-q',
                '-p', '20',
                '-b', str(size),
                '-C', str(self.PACKET_COUNT),
            ]

            self.logger.info("Performing ICMP ECHO RTT measurements with %d byte packets to %d nodes." % (size, len(node_ips)))
            process = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                close_fds=True,
            )
            processes.append(process)

            def communicator(node_ips, size, process):
                t0 = timezone.now()
                data = process.communicate(("\n".join(node_ips)) + '\n')[0]
                t1 = timezone.now()
                outputs.append((size, [x.split() for x in data.strip().split('\n')]))
                metadata.append((size, t0, t1))

            thread = threading.Thread(target=communicator, args=(node_ips, size, process))
            thread.daemon = True
            threads.append(thread)
            thread.start()

        for t in threads:
            t.join()
        for p in processes:
            try:
                p.kill()
            except OSError:
                pass

        self.logger.info("All ICMP ECHO RTT measurements completed.")

        context.rtt.meta = {}
        for size, start, end in metadata:
            context.rtt.meta[size] = {
                'start': start,
                'end': end,
            }

        context.rtt.results = {}
        for size, results in outputs:
            for result in results:
                try:
                    node_ip = ipaddr.IPAddress(result[0])
                except ValueError:
                    # fping error message for a specific packet
                    continue

                try:
                    rtt = [float(x) for x in result[2:] if x != '-']
                except ValueError:
                    # TODO: Handle output for duplicate packets
                    continue

                n = len(rtt)
                s = sum(rtt)
                ss = sum([x ** 2 for x in rtt])

                if n == 0:
                    std = None
                elif n == 1:
                    std = 0.0
                else:
                    std = math.sqrt((float(n) * ss - s ** 2) / (n * (n - 1)))

                context.rtt.results.setdefault(str(node_ip), {})[size] = {
                    'sent': self.PACKET_COUNT,
                    'successful': n,
                    'failed': max(0, self.PACKET_COUNT - n),
                    'rtt_min': min(rtt) if rtt else None,
                    'rtt_max': max(rtt) if rtt else None,
                    'rtt_avg': (float(s) / n) if rtt else None,
                    'rtt_std': std,
                }

        return context, nodes


class StoreNode(monitor_processors.NodeProcessor):
    """
    A processor that stores per-node RTT measurement results.
    """

    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        try:
            router_id = node.config.core.routerid(queryset=True).get(family='ipv4').router_id
            results = context.rtt.results.get(router_id, None)
            if not results:
                return context

            # Store results into monitoring schema
            for size, result in results.iteritems():
                rm, _ = monitor_models.RttMeasurementMonitor.objects.get_or_create(
                    root=node,
                    packet_size=size,
                    source=context.rtt.source_node,
                )
                rm.start = context.rtt.meta[size]['start']
                rm.end = context.rtt.meta[size]['end']
                rm.all_packets = result['sent']
                rm.successful_packets = result['successful']
                rm.failed_packets = result['failed']
                rm.rtt_minimum = result['rtt_min']
                rm.rtt_average = result['rtt_avg']
                rm.rtt_maximum = result['rtt_max']
                rm.rtt_std = result['rtt_std']
                rm.packet_loss = 100 * rm.failed_packets / rm.all_packets
                rm.save()
        except core_models.RouterIdConfig.DoesNotExist:
            # No router-id for this node can be found for IPv4; this means
            # that we have nothing to do here
            pass

        return context
