import io
import logging
import time
from pathlib import Path
from typing import List
from uuid import uuid4

from src.accessors.ansible_accessor import AnsibleAccessor
from src.accessors.docker_accessor import DockerAccessor
from src.accessors.git_accessor import GitAccessor
from src.accessors.remote_accessor import RemoteAccessor
from src.celery_farmer import celery_app
from src.testing.runner import TestRunner

logger = logging.getLogger()


def prepare(git_url: str, ident: str):
    git_accessor = GitAccessor()
    git_accessor.pull_repository(
        git_url,
        ident
    )
    logger.info("pulled repository")
    docker_bridge = DockerAccessor()

    docker_bridge.build_image(
        f"dane4kq/testing_padawan:{ident}",
        repo_path=Path(f"./{ident}")
    )
    logger.info("built image")
    docker_bridge.push_image(ident)
    logger.info("pushed image")
    # dane4kq/testing_padawan

    compose_file = DockerAccessor.build_docker_compose(
        f"dane4kq/testing_padawan:{ident}",
        database_envs={
            "POSTGRES_DB": "postgres",
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "postgres"
        },
        python_image_envs={
            "DB_NAME": "postgres",
            "DB_USER": "postgres",
            "DB_PASSWORD": "postgres",
            "DB_HOST": "database",
            "DB_PORT": 5432,
            "POSTGRES_DB": "postgres",
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "postgres"
        }
    )
    logger.info("built docker compose")
    remote_accessor = RemoteAccessor(
        "127.0.0.1",
        "/Users/dane4kq/PycharmProjects/padawan-web-worker/config/id_rsa"
    )

    remote_accessor.push_file_to_remote(
        io.BytesIO(compose_file),
        "/tmp/docker-compose.yml"
    )
    logger.info("create docker-compose")
    ansible_accessor = AnsibleAccessor()

    ansible_accessor.start_docker_compose("/tmp")
    logger.info("started docker compose")
    return git_accessor, docker_bridge, remote_accessor, ansible_accessor


def clean_up(git_accessor: GitAccessor, docker_bridge: DockerAccessor, remote_accessor: RemoteAccessor,
             ansible_accessor: AnsibleAccessor, ident: str):
    ansible_accessor.down_docker_compose("/tmp")
    git_accessor.delete_local_repository(ident)
    docker_bridge.remove_image_localy(f"dane4kq/testing_padawan:{ident}")
    remote_accessor.remove_file_from_remote("/tmp/docker-compose.yml")


@celery_app.task(name='remote.test_api_submission')
def test_api_submission(submission_id: int, scenarios: List[dict], git_url: str):
    print(submission_id)
    print(scenarios)
    print(git_url)

    ident = str(uuid4())[:8]

    git_accessor, docker_bridge, remote_accessor, ansible_accessor = prepare(git_url, ident)
    time.sleep(10)
    test_runner = TestRunner(
        submission_id=submission_id,
        scenarios=scenarios
    )
    test_runner.run()
    test_runner.create_result_data()
    clean_up(git_accessor, docker_bridge, remote_accessor, ansible_accessor, ident)
