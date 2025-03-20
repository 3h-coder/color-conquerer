import { MatchActionDto } from "../dto/actions/MatchActionDto";
import { PartialSpellDto } from "../dto/spell/PartialSpellDto";
import { localStorageKeys } from "../env";
import { developmentErrorLog } from "../utils/loggingUtils";

export function handleSpellCastingAnimation(action: MatchActionDto, setActionSpell: (spellAction: PartialSpellDto | null) => void, isMyTurn: boolean) {
    const spellAction = action.spell;
    if (!spellAction) {
        developmentErrorLog(`The spell of the action was ${spellAction}, cannot animate`);
        return;
    }

    const cleanupDelayInMs = 3500;

    const spellActionDescriptionTitle = isMyTurn ? "You used" : "Your opponent used";
    localStorage.setItem(localStorageKeys.playPage.spellActionDescription, spellActionDescriptionTitle);
    setActionSpell(spellAction);
    setTimeout(() => {
        setActionSpell(null);
    }, cleanupDelayInMs);
}