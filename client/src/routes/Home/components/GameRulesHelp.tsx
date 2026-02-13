import { useEffect, useRef, useState } from "react";
import { InfoIcon } from "../../../assets/svg";
import SingleButtonModal from "../../../components/modals/SingleButtonModal";
import { bindTooltip, TooltipPosition } from "../../../singletons/tooltip";

const RULES = [
    "1v1 matches, turn based.",
    "Fixed 11 by 11 square grid, where cells are the individual grid squares that may be controlled by a player.",
    "A player wins when their opponent's health reaches 0.",
    "Master cells (deep blue and red cells) represent their respective player. Basically, the blue team is you and the red team is your opponent.",
    "A player loses HP whenever their master cell takes damage.",
    "Players begin with 1 mana point each, and gain an additional one each turn until they reach a maximum of 9.",
    "Mana points can be used to spawn cells or cast spells.",
    "Cells can move or attack each turn, except the turn where they were spawned.",
    "Starting from their second turn, players lose 1 stamina point per turn. Once they arrive at 0 stamina, they enter the fatigue state and start taking damage at the beginning of each turn.",
    "Fatigue damage gradually increases over the turns, incremented by 1 (first 1 damage, then 2, 3, etc.).",
    "Spells are special actions that players may use directly from their action bar.",
    "Spells allow the player to restore their stamina (1 spell casting = 1 stamina point restored).",
    "Each spell can only be cast a fixed number of times during the match.",
];

export default function GameRulesHelp() {
    const gameRulesIconRef = useRef<HTMLDivElement | null>(null);
    const gameRulesRef = useRef<HTMLUListElement | null>(null);
    const [showGameRules, setShowGameRules] = useState(false);
    const [animatedIndexes, setAnimatedIndexes] = useState<number[]>([]);

    useEffect(() => {
        const cleanup = bindTooltip(gameRulesIconRef, {
            position: TooltipPosition.TOP_RIGHT,
            tooltipText: "Click to view game rules",
        });

        return cleanup;
    }, []);

    useEffect(() => {
        if (!showGameRules) {
            setAnimatedIndexes([]);
            return;
        }

        setAnimatedIndexes([]); // Reset before animating

        RULES.forEach((_, index) => {
            setTimeout(() => {
                setAnimatedIndexes((prev) => [...prev, index]);
            }, index * 35);
        });
    }, [showGameRules]);

    return (
        <>
            <div
                id="game-rules"
                ref={gameRulesIconRef}
                onClick={() => setShowGameRules(true)}
            >
                <InfoIcon />
            </div>
            <SingleButtonModal
                isOpenState={[showGameRules, setShowGameRules]}
                title="Game Rules"
                buttonText="Got it"
                onClose={() => setShowGameRules(false)}
                style={{ backgroundColor: "var(--deep-blue)" }}
            >
                <ul id="game-rules-list" ref={gameRulesRef}>
                    {RULES.map((rule, index) => (
                        <li
                            key={index}
                            style={{
                                opacity: animatedIndexes.includes(index) ? 1 : 0,
                                animation: animatedIndexes.includes(index)
                                    ? "fade-in 0.3s ease-in-out"
                                    : "none",
                            }}
                        >
                            {rule}
                        </li>
                    ))}
                </ul>
            </SingleButtonModal>
        </>
    );
}
