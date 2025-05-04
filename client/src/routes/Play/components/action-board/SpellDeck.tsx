import { useTurnContext } from "../../../../contexts/TurnContext";
import { SpellDto } from "../../../../dto/spell/SpellDto";
import SpellCard from "./SpellCard";

export default function SpellDeck() {
    const { turnContext } = useTurnContext();
    const spells = turnContext.gameContext.spellsDto.spells;

    return (
        <div className="spell-deck">
            {spells.map((spell: SpellDto, index: number) => (
                <SpellCard key={index} spell={spell} />
            ))}
        </div>
    );
}