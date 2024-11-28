import { usePlayerInfo } from "../../../contexts/PlayerContext";
import { useTurnInfo } from "../../../contexts/TurnContext";
import PlayerHPAndMPInfo from "./PlayerHPAndMPInfo";

export default function MyPlayerInfo() {
    const { isPlayer1 } = usePlayerInfo();
    const { turnInfo } = useTurnInfo();
    const playerGameInfo = isPlayer1
        ? turnInfo.playerInfoBundle.player1GameInfo
        : turnInfo.playerInfoBundle.player2GameInfo;

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
