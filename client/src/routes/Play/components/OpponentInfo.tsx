import { usePlayerInfo } from "../../../contexts/PlayerContext";
import { useTurnInfo } from "../../../contexts/TurnContext";
import PlayerHPAndMPInfo from "./PlayerHPAndMPInfo";

export default function OpponentInfo() {
    const { isPlayer1 } = usePlayerInfo();
    const { turnInfo } = useTurnInfo();
    const opponentGameInfo = isPlayer1
        ? turnInfo.playerInfoBundle.player2GameInfo
        : turnInfo.playerInfoBundle.player1GameInfo;

    return (
        <PlayerHPAndMPInfo
            currentHP={opponentGameInfo.currentHP}
            maxHP={opponentGameInfo.maxHP}
            currentMP={opponentGameInfo.currentMP}
            maxMP={opponentGameInfo.maxMP}
        />
    );
}
