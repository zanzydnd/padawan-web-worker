from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json
import logging
import shutil
import subprocess

import ansible.constants as C

from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory.manager import InventoryManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.playbook import Play
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager

from src.core.settings import settings
from ansible import context

logger = logging.getLogger()


class ResultsCollectorJSONCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in.

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin.
    """

    def __init__(self, *args, **kwargs):
        super(ResultsCollectorJSONCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.host_unreachable[host.get_name()] = result
        print(result._result)

    def v2_runner_on_ok(self, result, *args, **kwargs):
        """Print a json representation of the result.

        Also, store the result in an instance attribute for retrieval later
        """
        host = result._host
        self.host_ok[host.get_name()] = result
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_failed(self, result, *args, **kwargs):
        host = result._host
        self.host_failed[host.get_name()] = result
        print(result._result)


class AnsibleAccessor:
    def __init__(self):
        context.CLIARGS = ImmutableDict(connection='ssh',  # module_path=['/to/mymodules', '/usr/share/ansible'],
                                        forks=10, become=True,
                                        module_path=None,
                                        remote_user="root",
                                        private_key_file="/Users/dane4kq/.ssh/id_rsa",
                                        become_method="sudo", become_user="root", check=False, diff=False, verbosity=0)

        sources = ",".join(settings.HOST_LIST)

        if len(settings.HOST_LIST) == 1:
            sources += ','

        self.loader = DataLoader()

        results_callback = ResultsCollectorJSONCallback()
        passwords = dict(vault_pass='secret')

        self.inventory = InventoryManager(loader=self.loader, sources=sources)
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)
        self.tqm = TaskQueueManager(
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            stdout_callback=results_callback,
            passwords=passwords
        )

    def run_play(self, play_source: dict):
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        print(play)
        try:
            result = self.tqm.run(play)
            print(result)
        finally:
            self.tqm.cleanup()
            if self.loader:
                self.loader.cleanup_all_tmp_files()

        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

    def start_docker_compose(self, compose_dir):
        # TODO: переписать на ansible
        p = subprocess.Popen(["docker-compose", "up", "-d"], cwd=compose_dir)
        p.wait()

    def down_docker_compose(self, compose_dir):
        # TODO: переписать на ansible
        p = subprocess.Popen(["docker-compose", "down"], cwd=compose_dir)
        p.wait()
    # def start_docker_compose(self, compose_dir):
    #     logger.info(f"Starting compose file. compose_dir:{compose_dir}")
    #     play_source = dict(
    #         name="Deploy service Play",
    #         hosts=settings.HOST_LIST,
    #         gather_facts='yes',
    #         tasks=[
    #             dict(
    #                 name="Starting compose",
    #                 action=dict(
    #                     module='community.docker.docker_compose',
    #                     project_src=compose_dir,
    #                 ),
    #                 register='shell_out',
    #             ),
    #         ]
    #     )
    #     # play_source = dict(
    #     #     name="Ansible Play",
    #     #     hosts=settings.HOST_LIST,
    #     #     gather_facts='no',
    #     #     tasks=[
    #     #         dict(action=dict(module='shell', args='ls'), register='shell_out'),
    #     #         dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}'))),
    #     #         dict(action=dict(module='command', args=dict(cmd='/usr/bin/uptime'))),
    #     #     ]
    #     # )
    #     self.run_play(play_source)
    #
    # def down_docker_compose(self, compose_dir):
    #     logger.info("Downing compose file")
    #     play_source = dict(
    #         name="Stop service Play",
    #         hosts=settings.HOST_LIST,
    #         gather_facts='yes',
    #         tasks=[
    #             dict(
    #                 name="Stopping compose",
    #                 action=dict(
    #                     module='community.docker.docker_compose',
    #                     project_src=compose_dir,
    #                     build="false",
    #                     stopped="true",
    #                 ),
    #                 register='shell_out',
    #             ),
    #             dict(
    #                 name="Deleting compose",
    #                 action=dict(
    #                     module='community.docker.docker_compose',
    #                     project_src=compose_dir,
    #                     build="false",
    #                     remove_images="all",
    #                     remove_orphans="true",
    #                 ),
    #                 register='shell_out',
    #             ),
    #         ]
    #     )
    #     self.run_play(play_source)
