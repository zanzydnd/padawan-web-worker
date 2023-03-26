import os


class Settings:
    HOST_LIST = ["176.119.147.94", ]
    REDIS_URL = "redis://localhost:6379/0"
    DOCKER_LOGIN = os.getenv("DOCKER_LOGIN")
    DOCKER_PASSWORD = os.getenv("DOCKER_PASSWORD")


settings = Settings()
