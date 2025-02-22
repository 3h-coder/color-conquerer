import { MatchActionDto } from "../dto/MatchActionDto";
import { PartialSpellDto } from "../dto/PartialSpellDto";
import { developmentErrorLog } from "../utils/loggingUtils";

export function handleSpellCastingAnimation(action: MatchActionDto, setActionSpell: (spellAction: PartialSpellDto | null) => void) {
    const spellAction = action.spell;
    if (!spellAction) {
        developmentErrorLog(`The spell of the action was ${spellAction}, cannot animate`);
        return;
    }

    const cleanupDelayInMs = 3500;

    setActionSpell(spellAction);
    setTimeout(() => {
        setActionSpell(null);
    }, cleanupDelayInMs);
}