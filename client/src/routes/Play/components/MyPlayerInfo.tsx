import { usePlayerInfo } from "../../../contexts/PlayerContext";
import { usePlayersGameInfo } from "../../../contexts/PlayersGameInfoContext";
import PlayerHPAndMPInfo from "./PlayerHPAndMPInfo";

export default function MyPlayerInfo() {
    const { isPlayer1 } = usePlayerInfo();
    const { playerGameInfoBundle } = usePlayersGameInfo();

    const playerGameInfo = isPlayer1
        ? playerGameInfoBundle.player1GameInfo
        : playerGameInfoBundle.player2GameInfo;

    return (
        <PlayerHPAndMPInfo
            currentHP={playerGameInfo.currentHP}
            currentMP={playerGameInfo.currentMP}
            maxHP={playerGameInfo.maxHP}
            maxMP={playerGameInfo.maxMP}
            hpFirst={true}
        />
    );
}
