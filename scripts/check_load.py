#!/usr/bin/env python

import nagiosplugin

class Load(nagiosplugin.Resource):
    """Domain model: system load.

    Determines the system load parameters and (optionally) cpu count.
    The `probe` method returns the three standard load average numbers.
    If `percpu` is true, the load average will be normalized.

    This check requires Linux-style /proc files to be present.
    """

    def __init__(self, percpu=False):
        self.percpu = percpu

    def cpus(self):
        _log.info('counting cpus with "nproc"')
        cpus = int(subprocess.check_output(['nproc']))
        _log.debug('found %i cpus in total', cpus)
        return cpus

    def probe(self):
        _log.info('reading load from /proc/loadavg')
        with open('/proc/loadavg') as loadavg:
            load = loadavg.readline().split()[0:3]
        _log.debug('raw load is %s', load)
        cpus = self.cpus() if self.percpu else 1
        load = [float(l) / cpus for l in load]
        for i, period in enumerate([1, 5, 15]):
            yield nagiosplugin.Metric('load%d' % period, load[i], min=0,
                                      context='load')
