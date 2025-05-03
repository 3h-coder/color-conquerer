import { useEffect, useRef, useState } from "react";
import { PlayerResourcesDto } from "../../../../dto/player/PlayerResourcesDto";
import { EMPTY_STRING } from "../../../../env";
import { bindTooltip } from "../../../../singletons/tooltip";
import { delay } from "../../../../utils/domUtils";
import "./styles/PlayerHPAndMPInfo.css";


interface PlayerResourcesInfoProps {
    playerResourcesDto: PlayerResourcesDto;
    own: boolean;
}

export default function PlayerResourcesInfo(props: PlayerResourcesInfoProps) {
    const { playerResourcesDto, own } = props;
    const { currentHP, maxHP, currentMP, maxMP, currentStamina, maxStamina } = playerResourcesDto;
    return (
        <div className="player-resources-container">
            {own ? <PlayerHP currentHP={currentHP} maxHP={maxHP} /> : <></>}
            <PlayerStamina currentStamina={currentStamina} maxStamina={maxStamina} />
            <PlayerMP currentMP={currentMP} maxMP={maxMP} />
            {!own ? <PlayerHP currentHP={currentHP} maxHP={maxHP} /> : <></>}
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
    const [animate, setAnimate] = useState(false);
    const prevHP = useRef<number | undefined>(undefined);
    const percentage = Math.round((currentHP * 100) / maxHP);
    const hpText = `${currentHP}/${maxHP}`;

    useEffect(() => {
        handleHPChange();

        async function handleHPChange() {
            if (!prevHP.current) {
                prevHP.current = currentHP;
                return;
            }

            if (prevHP.current !== currentHP) {
                setAnimate(true);
                await delay(1000);
                setAnimate(false);
            }

            prevHP.current = currentHP;
        }
    }, [currentHP]);

    return (
        <div className="hp-container">
            <span>{hpText}</span>
            <div className="hp-circle-container-outer">
                <div
                    className={`hp-circle-container-inner${animate ? " hp-animate-bg" : ""}`}
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
    const ref = useRef<HTMLDivElement>(null);
    const { currentStamina, maxStamina } = props;
    const percentage = Math.round((currentStamina * 100) / maxStamina);

    useEffect(() => {
        const tooltipText = "Stamina depletes at the beginning of each turn. Cast spells to gain some back and not die from fatigue.";
        if (!ref.current)
            return;

        return bindTooltip(ref, {
            tooltipText: tooltipText,
        });
    }, [ref]);

    return (
        <div className="stamina-container" ref={ref}>
            <div className="stamina-container-inner" style={{ width: `${percentage}%`, opacity: percentage > 0 ? "1" : "0" }} />
            <span className="stamina-count">{currentStamina}</span>
        </div>
    );
}