# coding=utf-8

"""
Uses /proc/loadavg to collect data on load average

#### Dependencies

 * /proc/loadavg

"""

import diamond.collector
import re
import os
import multiprocessing
from diamond.collector import str_to_bool


class MFMS_LoadAverageCollector(diamond.collector.Collector):

    PROC_LOADAVG = '/proc/loadavg'
    PROC_LOADAVG_RE = re.compile(r'([\d.]+) ([\d.]+) ([\d.]+) (\d+)/(\d+)')

    def get_default_config_help(self):
        config_help = super(MFMS_LoadAverageCollector,
                            self).get_default_config_help()
        config_help.update({
            'simple':   'Only collect the 1 minute load average'
        })
        return config_help

    def get_default_config(self):
        """
        Returns the default collector settings
        """
        config = super(MFMS_LoadAverageCollector, self).get_default_config()
        config.update({
            'path':     'intel.psutil.load',
            'simple':   'False'
        })
        return config

    def collect(self):
        load01, load05, load15 = os.getloadavg()
        cpu_count = multiprocessing.cpu_count()

        if not str_to_bool(self.config['simple']):
            self.publish_gauge('load1', load01, 2)
            self.publish_gauge('load5', load05, 2)
            self.publish_gauge('load15', load15, 2)
        else:
            self.publish_gauge('load', load01, 2)

        # Legacy: add process/thread counters provided by
        # /proc/loadavg (if available).
        if os.access(self.PROC_LOADAVG, os.R_OK):
            file = open(self.PROC_LOADAVG)
            for line in file:
                match = self.PROC_LOADAVG_RE.match(line)
                if match:
                    self.publish_gauge('processes_running',
                                       int(match.group(4)))
                    self.publish_gauge('processes_total', int(match.group(5)))
            file.close()
