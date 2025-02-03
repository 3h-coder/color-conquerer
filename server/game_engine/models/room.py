from dataclasses import dataclass


@dataclass
class Room:
    id: str
    session_ids: dict[str, str]
