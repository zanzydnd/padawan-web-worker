from pathlib import Path

from accessors.docker_accessor import DockerAccessor
from accessors.git_accessor import GitAccessor

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
