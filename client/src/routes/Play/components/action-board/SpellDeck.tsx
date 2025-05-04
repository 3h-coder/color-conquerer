import { useGameContext } from "../../../../contexts/GameContext";
import { SpellDto } from "../../../../dto/spell/SpellDto";
import SpellCard from "./SpellCard";

export default function SpellDeck() {
    const { gameContext } = useGameContext();
    const spells = gameContext.spellsDto.spells;

    return (
        <div className="spell-deck">
            {spells.map((spell: SpellDto, index: number) => (
                <SpellCard key={index} spell={spell} />
            ))}
        </div>
    );
}