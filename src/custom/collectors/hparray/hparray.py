# coding=utf-8

import diamond.collector
from diamond.collector import str_to_bool
import subprocess
import os
import StringIO

class MFMS_HPArrayCollector(diamond.collector.Collector):

    def get_default_config_help(self):
        config_help = super(MFMS_HPArrayCollector, self).get_default_config_help()
        config_help.update({
            'hpacucli_exe': 'The path to hpacucli utility',
            'use_sudo': 'Call hpacucli using sudo',
            'sudo_exe': 'The path to sudo',
            'sudo_user': 'The user to use if using sudo',
        })
        return config_help

    def get_default_config(self):
        config = super(MFMS_HPArrayCollector, self).get_default_config()
        config.update({
            'path': 'mfms.hpacucli',
            'hpacucli_exe': '/opt/HPQacucli/sbin/hpacucli',
            'use_sudo': False,
            'sudo_exe': '/usr/bin/sudo',
            'sudo_user': '',
        })
        return config

    def collect(self):
        try:
            if str_to_bool(self.config['use_sudo']):
                cmdline = [
                    self.config['sudo_exe'], '-u', self.config['sudo_user'],
                    '--', self.config['hpacucli_exe'], 'ctrl', 'all', 'show', 'config', 'detail'
                ]
            else:
                cmdline = [self.config['hpacucli_exe'], 'ctrl', 'all', 'show', 'config', 'detail']

            proc = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            lines = StringIO.StringIO(output)
            res = []
            while True:
                line = lines.readline()
                if line == '':
                    break
                if line.find('physicaldrive') >= 0:
                    obj = {}
                    while True:
                        partline = lines.readline()
                        kv = partline.split(':')
                        if kv[0] == partline:
                            break
                        obj[kv[0].strip()] = kv[1].strip()
                    res.append(obj)

            for r in res:
                value = 0 if r['Status'] == 'OK' else 1
                name = '%s:%s:%s' % (r['Port'], r['Box'], r['Bay'])
                self.publish('%s.%s.%s' % (name, r['Serial Number'], 'health'), value, precision=0, metric_prefix=self.config['path'])

        except OSError as err:
            self.log.error("Could not run %s: %s",
                           self.config['amavisd_exe'],
                           err)
            return None

        return True