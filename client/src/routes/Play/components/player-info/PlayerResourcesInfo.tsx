import { PlayerResourcesDto } from "../../../../dto/player/PlayerResourcesDto";
import { EMPTY_STRING } from "../../../../env";
import "./styles/PlayerHPAndMPInfo.css";


interface PlayerResourcesInfoProps {
    playerResourcesDto: PlayerResourcesDto;
    hpFirst?: boolean;
}

export default function PlayerResourcesInfo(props: PlayerResourcesInfoProps) {
    const { playerResourcesDto, hpFirst } = props;
    const { currentHP, maxHP, currentMP, maxMP } = playerResourcesDto;
    return (
        <div className="player-resources-container">
            {hpFirst ? <PlayerHP currentHP={currentHP} maxHP={maxHP} /> : <></>}
            <PlayerStamina currentStamina={currentHP} maxStamina={maxHP} />
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

interface PlayerStaminaProps {
    currentStamina: number;
    maxStamina: number;
}

function PlayerStamina(props: PlayerStaminaProps) {
    const { currentStamina, maxStamina } = props;
    const percentage = Math.round((currentStamina * 100) / maxStamina);

    return (
        <div className="stamina-container">
            <div className="stamina-container-inner" style={{ width: `${percentage}%` }} />
        </div>
    );
}