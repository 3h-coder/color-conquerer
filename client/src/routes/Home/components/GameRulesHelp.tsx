import { useEffect, useRef, useState } from "react";
import { InfoIcon } from "../../../assets/svg";
import SingleButtonModal from "../../../components/modals/SingleButtonModal";
import { bindTooltip, TooltipPosition } from "../../../singletons/tooltip";

export default function GameRulesHelp() {
    const gameRulesRef = useRef<HTMLDivElement | null>(null);
    const [showGameRules, setShowGameRules] = useState(false);

    useEffect(() => {
        const cleanup = bindTooltip(gameRulesRef, {
            position: TooltipPosition.TOP_RIGHT,
            tooltipText: "Click to view game rules",
        });

        return cleanup;
    }, []);

    return (
        <>
            <div id="game-rules" ref={gameRulesRef} onClick={() => setShowGameRules(true)}>
                <InfoIcon />
            </div>
            <SingleButtonModal isOpenState={[showGameRules, setShowGameRules]} title="Game Rules" buttonText="Got it" onClose={() => setShowGameRules(false)}>
                <ul id="game-rules-list">
                    <li>1v1 matches, turn based.</li>
                    <li>Fixed 11 by 11 square grid, where cells are the individual grid squares that may be controlled by a player.</li>
                    <li>A player wins when their opponent's health reaches 0.</li>
                    <li>Master cells (deep blue and red cells) represent their respective player. Basically, the blue team is you and the red team is your opponent.</li>
                    <li>A player loses HP whenever their master cell takes damage.</li>
                    <li>Players begin with 1 mana point each, and gain an additional one each turn until they reach a maximum of 9.</li>
                    <li>Mana points can be used to spawn cells or cast spells.</li>
                    <li>Cells can move or attack each turn, except the turn where they were spawned.</li>
                    <li>Starting from their second turn, players lose 1 stamina point per turn. Once they arrive at 0 stamina, they enter the fatigue state and start taking damage at the beginning of each turn.</li>
                    <li>Fatigue damage gradually increases over the turns, incremented by 1 (first 1 damage, then 2, 3, etc.).</li>
                    <li>Spells are special actions that players may use directly from their action bar.</li>
                    <li>Spells allow the player to restore their stamina (1 spell casting = 1 stamina point restored).</li>
                    <li>Each spell can only be cast a fixed number of times during the match.</li>
                </ul>
            </SingleButtonModal>
        </>

    );
}