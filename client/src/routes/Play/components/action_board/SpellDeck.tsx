import { usePlayerInfo } from "../../../../contexts/PlayerContext";
import { useTurnInfo } from "../../../../contexts/TurnContext";
import { SpellDto } from "../../../../dto/SpellDto";
import SpellCard from "../buttons/SpellCard";

export default function SpellDeck() {
    const { turnInfo } = useTurnInfo();
    const { isPlayer1 } = usePlayerInfo();
    const playerGameInfo = isPlayer1 ? turnInfo.playerResourceBundle.player1Resources : turnInfo.playerResourceBundle.player2Resources;
    const spells = playerGameInfo.spells;

    return (
        <div className="spell-deck">
            {spells.map((spell: SpellDto, index: number) => (
                <SpellCard key={index} spell={spell} />
            ))}
        </div>
    );
}