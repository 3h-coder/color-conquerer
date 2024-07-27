from dataclasses import asdict, dataclass


@dataclass
class BaseDto:
    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
