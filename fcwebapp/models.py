from uuid import UUID


class UserInfo:
    def __init__(self, uuid: UUID, username: str, name: str, email: str, occupying_uuid: UUID=None):
        self.uuid: UUID = uuid
        self.username = username
        self.name = name
        self.email = email
        self.first_name = name.split()[0]
        self.occupying_uuid = occupying_uuid
        self.met_requirements = self.occupying_uuid is not None

    def __eq__(self, other) -> bool:
        if isinstance(other, UserInfo):
            return self.uuid == other.uuid
        return False

    def __str__(self):
        return self.username + ': ' + str(self.occupying_uuid) + ' ' + str(self.met_requirements)


class Tent:
    def __init__(self, uuid: UUID, name: str, capacity: int, occupants: list[UserInfo] = None):
        self.uuid: UUID = uuid
        self.name = name
        self.capacity = capacity
        if not occupants:
            occupants = []
        self.occupants = occupants

    def add_occupant(self, user: UserInfo):
        self.occupants.append(user)

    def remove_occupant(self, user: UserInfo):
        self.occupants.remove(user)


class Hammock:
    def __init__(self, uuid: UUID, name: str, occupant: UserInfo):
        self.uuid: UUID = uuid
        self.name = name
        self.occupant = occupant

    def __str__(self):
        return '{'+str(self.uuid)+'} '+ self.name +' '+self.occupant.name


users:dict[UUID, UserInfo] = {}
tents:dict[UUID,Tent] = {}
hammocks:dict[UUID, Hammock] = {}