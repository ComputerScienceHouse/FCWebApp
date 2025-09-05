from uuid import UUID


class UserInfo:
    def __init__(
            self,
            uuid: UUID,
            username: str,
            name: str,
            email: str,
            occupying_uuid: UUID = None,
            phone_number: str = None,
            in_ride: bool = False,
            diet: str = None,
            allergies: str = None,
            health: str = None,
    ):
        self.uuid: UUID = uuid
        self.username = username
        self.name = name
        self.email = email
        self.first_name = name.split()[0]
        self.occupying_uuid = occupying_uuid
        self.phone_number = phone_number
        self.in_ride = in_ride
        self.diet = diet
        self.allergies = allergies
        self.health = health
        self.met_requirements = False
        self.check()

    def check(self):
        self.met_requirements = self.occupying_uuid is not None and self.phone_number != "" and self.in_ride
        # TODO: Make diet and allergies arrays (so eventually a database can search by allergy)

    def __eq__(self, other) -> bool:
        if isinstance(other, UserInfo):
            return self.uuid == other.uuid
        return False

    def __str__(self):
        return (
                self.username
                + ": "
                + str(self.occupying_uuid)
                + " "
                + str(self.met_requirements)
        )


class Tent:
    def __init__(
            self, uuid: UUID, name: str, capacity: int, occupants: list[UserInfo] = None
    ):
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
        return "{" + str(self.uuid) + "} " + self.name + " " + self.occupant.name


users: dict[UUID, UserInfo] = {}
tents: dict[UUID, Tent] = {}
hammocks: dict[UUID, Hammock] = {}
