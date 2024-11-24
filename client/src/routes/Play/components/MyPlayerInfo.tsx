import { usePlayerInfo } from "../../../contexts/PlayerContext";
import PlayerHPAndMPInfo from "./PlayerHPAndMPInfo";

export default function MyPlayerInfo() {
    const { playerGameInfo } = usePlayerInfo();

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
