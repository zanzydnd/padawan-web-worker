import io
from pathlib import Path

from accessors.ansible_accessor import AnsibleAccessor
from accessors.docker_accessor import DockerAccessor
from accessors.git_accessor import GitAccessor
from accessors.remote_accessor import RemoteAccessor

git_accessor = GitAccessor()
git_accessor.pull_repository(
    "https://github.com/zanzydnd/kvartika_test",
    "random_hash"
)

docker_bridge = DockerAccessor()

docker_bridge.build_image(
    "dane4kq/testing_padawan:custom_ident",
    repo_path=Path("./random_hash")
)

docker_bridge.push_image()
# dane4kq/testing_padawan

compose_file = DockerAccessor.build_docker_compose(
    "dane4kq/testing_padawan:custom_ident",
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
print(compose_file)
remote_accessor = RemoteAccessor(
    "176.119.147.94",
    "/Users/dane4kq/PycharmProjects/padawan-web-worker/config/id_rsa"
)

remote_accessor.push_file_to_remote(
    io.BytesIO(compose_file),
    "/tmp/docker-compose.yml"
)

ansible_accessor = AnsibleAccessor()

ansible_accessor.start_docker_compose("/tmp")
