import { ContainerProps } from "../../../components/containers";
import { usePlayerInfo } from "../../../contexts/PlayerContext";
import PlayerHPAndMPInfo from "./PlayerHPAndMPInfo";

export default function OpponentInfo() {
    const { opponentGameInfo } = usePlayerInfo();

    return (
        <PlayerHPAndMPInfo
            currentHP={opponentGameInfo.currentHP}
            maxHP={opponentGameInfo.maxHP}
            currentMP={opponentGameInfo.currentMP}
            maxMP={opponentGameInfo.maxMP}
        />
    );
}
