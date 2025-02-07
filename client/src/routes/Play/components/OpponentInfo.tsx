import { usePlayerInfo } from "../../../contexts/PlayerContext";
import { usePlayersGameInfo } from "../../../contexts/PlayersGameInfoContext";
import PlayerHPAndMPInfo from "./PlayerHPAndMPInfo";

export default function OpponentInfo() {
    const { isPlayer1 } = usePlayerInfo();
    const { playerResourceBundle: playerGameInfoBundle } = usePlayersGameInfo();

    const opponentGameInfo = isPlayer1
        ? playerGameInfoBundle.player2Resources
        : playerGameInfoBundle.player1Resources;

    return (
        <PlayerHPAndMPInfo
            currentHP={opponentGameInfo.currentHP}
            maxHP={opponentGameInfo.maxHP}
            currentMP={opponentGameInfo.currentMP}
            maxMP={opponentGameInfo.maxMP}
        />
    );
}
