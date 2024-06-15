from dataclasses import dataclass, fields

import jsonpickle


@dataclass
class BaseDto:
    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in fields(self)}

    def to_json(self):
        return jsonpickle.encode(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
