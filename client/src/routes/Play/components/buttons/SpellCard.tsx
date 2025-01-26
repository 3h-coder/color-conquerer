import { useTurnInfo } from "../../../../contexts/TurnContext";
import { SpellDto } from "../../../../dto/SpellDto";

interface SpellCardProps {
    spell: SpellDto;
}

export default function SpellCard(props: SpellCardProps) {
    const { spell } = props;
    const { canInteract } = useTurnInfo();

    return (
        <button className="spell-card" disabled={!canInteract}>
            <div>{spell.manaCost}</div>
            <div>{spell.name}</div>
        </button>
    );

}