from dataclasses import dataclass, fields


@dataclass
class BaseDto:
    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in fields(self)}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
