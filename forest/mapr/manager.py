# -*- coding: utf-8 -*-


class MaprManager(object):
    ''' MaprManager is the core of Local or RPC API'''

    def run_jobflow(
            key_name=None,
            subnet_id=None,
            keep_alive=None,
            region_name=None,
            master_instance_type=None,
            slave_instance_type=None,
            termination_protected=None):
        '''
        Creates and starts running a new job flow.
        A maximum of 256 steps are allowed in each job flow.

        For long running job flows, we recommend that you periodically store
        your results. Also to prevent loss of data, configure the last step of
        the job flow to store results in OpenStack swift.
        
        parameter keep_jobflow_alive
        parameter termination_protected

        name **required**
        bootstrap_actions
        log_uri
        instances
        '''
        pass
    
    def add_instance_groups():
        '''
        Adds an instance group to a running cluster.
        ** Not supported **
        '''
        pass

    def add_jobflow_steps():
        '''
        Adds new steps to a running job flow.
        A maximum of 256 steps are allowed in eachjob flow.
        ** Not supported **
        '''
        pass

    def describe_jobflows():
        '''
        Returns a list of job flows that match all of the supplied parameters.
        '''
        pass

    def terminate_jobflows():
        pass

    def set_termination_protection():
        pass
