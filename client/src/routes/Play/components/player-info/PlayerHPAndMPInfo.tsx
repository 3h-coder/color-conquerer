import { EMPTY_STRING } from "../../../../env";


interface PlayerHPAndMPInfoProps {
    currentHP: number;
    maxHP: number;
    currentMP: number;
    maxMP: number;
    hpFirst?: boolean;
}

export default function PlayerHPAndMPInfo(props: PlayerHPAndMPInfoProps) {
    const { currentHP, maxHP, currentMP, maxMP, hpFirst } = props;
    return (
        <div className="player-mp-hp-container">
            {hpFirst ? <PlayerHP currentHP={currentHP} maxHP={maxHP} /> : <></>}
            <PlayerMP currentMP={currentMP} maxMP={maxMP} />
            {!hpFirst ? <PlayerHP currentHP={currentHP} maxHP={maxHP} /> : <></>}
        </div>
    );
}

interface PlayerMPProps {
    currentMP: number;
    maxMP: number;
}

function PlayerMP(props: PlayerMPProps) {
    const { currentMP, maxMP } = props;

    const manaPoints = Array.from({ length: maxMP }, (_, index) => (
        <ManaPoint key={index} isActive={index < currentMP} />
    ));

    return (
        <div className="mp-container">
            {manaPoints}
        </div>
    );
}

interface ManaPointProps {
    isActive: boolean;
}

function ManaPoint(props: ManaPointProps) {
    const { isActive } = props;
    return <div className={`mp ${isActive ? "active" : EMPTY_STRING}`} />;
}

interface PlayerHPProps {
    currentHP: number;
    maxHP: number;
}

function PlayerHP(props: PlayerHPProps) {
    const { currentHP, maxHP } = props;
    const percentage = Math.round((currentHP * 100) / maxHP);
    const hpText = `${currentHP}/${maxHP}`;

    return (
        <div className="hp-container">
            <span>{hpText}</span>
            <div className="hp-circle-container-outer">
                <div
                    className="hp-circle-container-inner"
                    style={{ height: `${percentage}%` }}
                >
                </div>
            </div>
        </div>
    );
}