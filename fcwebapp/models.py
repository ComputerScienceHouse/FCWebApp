from uuid import UUID


class UserInfo:
    def __init__(self, uuid:UUID, username:str, name:str,  email:str):
        self.uuid:UUID = uuid
        self.username = username
        self.name = name
        self.first_name = name.split()[0]
        self.met_requirements = False
