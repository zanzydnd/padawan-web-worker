import logging
import os
import shutil

from git import Repo

logger = logging.getLogger()


class GitAccessor:
    def pull_repository(self, repository_url: str, dir_name: str):
        logger.info("Cloning repo")
        Repo.clone_from(repository_url, f"./{dir_name}")

    def delete_local_repository(self, dir_name: str):
        logger.info("Removing repo")
        shutil.rmtree(dir_name, ignore_errors=True)

