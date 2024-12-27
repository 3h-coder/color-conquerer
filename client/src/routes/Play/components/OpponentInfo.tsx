import { usePlayerInfo } from "../../../contexts/PlayerContext";
import { usePlayersGameInfo } from "../../../contexts/PlayersGameInfoContext";
import PlayerHPAndMPInfo from "./PlayerHPAndMPInfo";

export default function OpponentInfo() {
    const { isPlayer1 } = usePlayerInfo();
    const { playerGameInfoBundle } = usePlayersGameInfo();

    const opponentGameInfo = isPlayer1
        ? playerGameInfoBundle.player2GameInfo
        : playerGameInfoBundle.player1GameInfo;

    return (
        <PlayerHPAndMPInfo
            currentHP={opponentGameInfo.currentHP}
            maxHP={opponentGameInfo.maxHP}
            currentMP={opponentGameInfo.currentMP}
            maxMP={opponentGameInfo.maxMP}
        />
    );
}
