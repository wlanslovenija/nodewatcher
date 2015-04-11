from django.conf import settings
from django.core import exceptions
from django.utils import importlib

from . import processors as monitor_processors


class MonitorConfig(object):
    """
    Stores configuration of monitoring runs.
    """

    def __init__(self):
        """
        Class constructor.
        """

        self._runs = {}
        self._discovered = False

    def discover(self):
        """
        Performs discovery of monitoring runs.
        """

        if self._discovered:
            return

        # TODO: Should we also support dynamic run registration?

        # Load monitor run definitions from the settings file.
        for run, config in settings.MONITOR_RUNS.iteritems():
            processors = []
            for proc_modules in config['processors']:
                # Support nested lists in order to make processor list reuse easier.
                if not isinstance(proc_modules, (list, tuple)):
                    proc_modules = [proc_modules]

                for proc_module in proc_modules:
                    i = proc_module.rfind('.')
                    module, attr = proc_module[:i], proc_module[i + 1:]
                    try:
                        module = importlib.import_module(module)
                        processor = getattr(module, attr)
                    except (ImportError, AttributeError):
                        raise exceptions.ImproperlyConfigured("Error importing monitoring processor %s!" % proc_module)

                    if not processors:
                        processors.append([processor])
                    else:
                        prev_class = processors[-1][-1]
                        curr_class = processor

                        # Consecutive node processors are grouped together so they will all be run in parallel
                        # on the list of nodes that has been prepared by recent network processor invocations.
                        if issubclass(prev_class, monitor_processors.NodeProcessor) and issubclass(curr_class, monitor_processors.NodeProcessor):
                            processors[-1].append(processor)
                        else:
                            processors.append([processor])

            run_info = {
                'name': run,
                'interval': config.get('interval', None),
                'workers': config.get('workers', None),
                'max_tasks_per_child': config.get('max_tasks_per_child', 100),
                'processors': processors,
            }

            # If no interval is configured, mark the run as on-demand.
            run_info['on_demand'] = run_info['interval'] is None

            self._runs[run] = run_info

        self._discovered = True

    def get_runs(self):
        """
        Returns a list of registered monitoring runs.
        """

        self.discover()

        return self._runs.values()

    def get_run(self, run):
        """
        Returns a descriptor for a specific registered monitoring run.

        :param run: Monitoring run identifier
        :return: Monitoring run descriptor
        """

        self.discover()

        # TODO: Error handling.
        return self._runs[run]

config = MonitorConfig()
