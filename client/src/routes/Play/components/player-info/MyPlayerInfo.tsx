import { usePlayerInfo } from "../../../../contexts/PlayerContext";
import { usePlayersGameInfo } from "../../../../contexts/PlayersGameInfoContext";
import PlayerHPAndMPInfo from "./PlayerHPAndMPInfo";

export default function MyPlayerInfo() {
    const { isPlayer1 } = usePlayerInfo();
    const { playerResourceBundle } = usePlayersGameInfo();

    const playerGameInfo = isPlayer1
        ? playerResourceBundle.player1Resources
        : playerResourceBundle.player2Resources;

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
