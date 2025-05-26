from dataclasses import asdict, dataclass

from dto.player.player_dto import PlayerDto


@dataclass
class SessionPlayer:
    player_id: str
    is_player1: str
    individual_room_id: str

    def to_dto(self):
        return PlayerDto(playerId=self.player_id, isPlayer1=self.is_player1)

    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        return cls(**data)

    def to_dict(self):
        return asdict(self)
