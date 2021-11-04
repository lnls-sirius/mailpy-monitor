import os
import json
import typing
import dataclasses
import docker.client
import docker.models.containers

from app.db import EntryData, GroupData

RESOURCES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../resources"
)


@dataclasses.dataclass(frozen=True)
class MongoContainerSettings:
    resources_path: str = RESOURCES_PATH
    name: str = "MONGODB_TEST_CONTAINER"
    port: int = 27017
    host: str = "localhost"
    database: str = "mailpy"
    root_username: str = "admin"
    root_password: str = "admin"
    username: str = "test"
    password: str = "test"
    image: str = "mongo:4.4.3-bionic"


class MongoContainerManager:
    def __init__(self, config: typing.Optional[MongoContainerSettings] = None):
        if not config:
            self.config = MongoContainerSettings()
        else:
            self.config = config

        self.docker_client = docker.client.DockerClient()
        self._container: typing.Optional[docker.models.containers.Container] = None

    def stop(self):
        if self._container:
            self._container.stop()
            self._container.remove()
        self.docker_client.close()

    def start(self):
        self.remove_previous_mongodb_containers()
        self._container = self.create_mongodb_container()
        self._container.start()

    def create_mongodb_container(self) -> docker.models.containers.Container:
        return self.docker_client.containers.create(
            self.config.image,
            name=self.config.name,
            environment={
                "MONGO_INITDB_DATABASE": self.config.database,
                "MONGO_INITDB_ROOT_USERNAME": self.config.root_username,
                "MONGO_INITDB_ROOT_PASSWORD": self.config.root_password,
                "MONGO_INITDB_USERNAME": self.config.username,
                "MONGO_INITDB_PASSWORD": self.config.password,
            },
            volumes=[
                f"{self.config.resources_path}/00-create-db-users.sh:/docker-entrypoint-initdb.d/00-create-db-users.sh:ro",
                f"{self.config.resources_path}/01-create-collections.js:/docker-entrypoint-initdb.d/01-create-collections.js:ro",
                f"{self.config.resources_path}/02-insert-data.sh:/docker-entrypoint-initdb.d/02-insert-data.sh:ro",
                f"{self.config.resources_path}/mailpy-db-2021-11-29:/mailpy-db-init-data:ro",
            ],
            ports={"27017/tcp": (self.config.host, self.config.port)},
            detach=True,
        )

    def remove_previous_mongodb_containers(self):
        for container in self.docker_client.containers.list(all=True):
            if container.name == self.config.name:
                container.stop()
                container.remove()


class MongoJsonLoader:
    def __init__(
        self,
        dirname: typing.Optional[str] = None,
        entries_filename: str = "entries.json",
        groups_filename: str = "groups.json",
    ):
        if not dirname:
            dirname = dirname = os.path.join(RESOURCES_PATH, "mailpy-db-2021-11-29")

        self.entries_filename = os.path.join(dirname, entries_filename)
        self.groups_filename = os.path.join(dirname, groups_filename)

    def load_groups(self):
        with open(self.groups_filename, "r") as file:
            data = json.load(file)
            if type(data) != list:
                raise RuntimeError(
                    f"Expected {data} to be a list, received {type(data)}"
                )

            groups = [self._create_group(d) for d in data]
            groups.sort(key=lambda x: x.id)
            return groups

    def _create_group(self, d):
        return GroupData(
            id=d["_id"]["$oid"],
            name=d["name"],
            enabled=d["enabled"],
            description=d.get("description", ""),
        )

    def load_entries(self):
        with open(self.entries_filename, "r") as file:
            data = json.load(file)
            if type(data) != list:
                raise RuntimeError(
                    f"Expected {data} to be a list, received {type(data)}"
                )
            entries = [self._create_entry(d) for d in data]
            entries.sort(key=lambda x: x.id)
            return entries

    def _create_entry(self, d):
        return EntryData(
            id=d["_id"]["$oid"],
            pvname=d["pvname"],
            emails=d["emails"].split(":"),
            condition=d["condition"],
            alarm_values=d["alarm_values"],
            unit=d["unit"],
            warning_message=d["warning_message"],
            subject=d["subject"],
            email_timeout=d["email_timeout"],
            group=d["group"],
        )
