import { ContainerProps } from "../../../components/containers";
import { usePlayerInfo } from "../../../contexts/PlayerContext";

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

interface PlayerHPAndMPInfoProps {
    currentHP: number;
    maxHP: number;
    currentMP: number;
    maxMP: number;
}

function PlayerHPAndMPInfo(props: PlayerHPAndMPInfoProps) {
    const { currentHP, maxHP, currentMP, maxMP } = props;
    return (
        <div className="player-mp-hp-container">
            <PlayerHP currentHP={currentHP} maxHP={maxHP} />
        </div>
    );
}

interface PlayerHPProps {
    currentHP: number;
    maxHP: number;
}

function PlayerHP(props: PlayerHPProps) {
    const { currentHP, maxHP } = props;
    const percentage = Math.round((currentHP * 100) / maxHP);

    return (
        <HpContainer>
            <div
                className="hp-container-inner"
                style={{ height: `${percentage}%` }}
            >
                <h3>{currentHP}</h3>
            </div>
        </HpContainer>
    );
}

function HpContainer(props: ContainerProps) {
    return <div className="hp-container-outer">{props.children}</div>;
}
