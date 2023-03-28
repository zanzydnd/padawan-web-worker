import logging

import yaml
import docker

from pathlib import Path

from docker.models.images import Image
from yaml import SafeDumper

from src.core.settings import settings

logger = logging.getLogger()


class DockerAccessor:
    def __init__(self):
        self.client = docker.DockerClient(
            base_url='unix:///var/run/docker.sock'
        )
        self.client.login(
            username=settings.DOCKER_LOGIN,
            password=settings.DOCKER_PASSWORD
        )

    @staticmethod
    def build_docker_compose(python_full_image_name: str, database_envs: dict, python_image_envs: dict):
        docker_compose_dict = {
            "version": "3",
            "networks": {
                "tester": None,
            },
            "services": {
                "database": {
                    "image": "postgres:13-alpine",
                    "ports": ["5555:5432", ],
                    "environment": database_envs,
                    "restart": "always",
                    "networks": ["tester", ]
                },
                "backend": {
                    "networks": ["tester", ],
                    "depends_on": ["database", ],
                    "image": python_full_image_name,
                    "ports": ["8002:8000", ],
                    "environment": python_image_envs
                }
            }
        }
        logger.info(f"docker compose: {docker_compose_dict}")
        SafeDumper.add_representer(
            type(None),
            lambda dumper, value: dumper.represent_scalar(u"tag:yaml.org,2002:null", "")
        )
        return yaml.safe_dump(docker_compose_dict, encoding="utf-8", allow_unicode=True)

    def build_image(self, identifier: str, repo_path: Path) -> Image:
        logger.info("building image")
        return self.client.images.build(
            path=str(repo_path.absolute()), gzip=False, tag=identifier
        )[0]

    def push_image(self,identifier:str):
        logger.info("pushing image")
        for line in self.client.images.push('dane4kq/testing_padawan', tag=identifier, stream=True, decode=True):
            print(line)

    def remove_image_localy(self, image_name):
        logger.info("removing image")
        self.client.images.remove(image_name, force=True)
