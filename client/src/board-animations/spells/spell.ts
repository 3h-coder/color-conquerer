import { MatchActionDto } from "../../dto/actions/MatchActionDto";
import { PartialSpellDto } from "../../dto/spell/PartialSpellDto";
import { SpellId } from "../../enums/spellId";
import { localStorageKeys } from "../../env";
import { developmentErrorLog } from "../../utils/loggingUtils";
import { handleAmbushAnimation } from "./ambush";
import { handleArcheryVowAnimation } from "./archeryVow";
import { handleCelerityAnimation } from "./celerity";
import { handleShieldFormationAnimation } from "./shieldFormation";

const SPELL_ANIMATION_HANDLERS: Record<SpellId, ((spellAction: MatchActionDto) => void) | null> = {
    [SpellId.SHIELD_FORMATION]: handleShieldFormationAnimation,
    [SpellId.CELERITY]: handleCelerityAnimation,
    [SpellId.ARCHERY_VOW]: handleArcheryVowAnimation,
    [SpellId.AMBUSH]: handleAmbushAnimation,
    [SpellId.MINE_TRAP]: null,
};

export function handleSpellCastingAnimation(
    spellAction: MatchActionDto,
    setActionSpell: (spellAction: PartialSpellDto | null) => void,
    isMyTurn: boolean
) {
    const spell = spellAction.spell;
    if (!spell) {
        developmentErrorLog(
            `The spell of the action was ${spell}, cannot animate`
        );
        return;
    }

    showSpellDetails(isMyTurn, setActionSpell, spell);
    handleSpellAnimation(spellAction);
}

function handleSpellAnimation(spellAction: MatchActionDto) {
    const spellId = spellAction.spell?.id;
    if (!spellId)
        return;

    const handler = SPELL_ANIMATION_HANDLERS[spellId as SpellId];
    if (handler) {
        handler(spellAction);
    }
}

function showSpellDetails(isMyTurn: boolean, setActionSpell: (spellAction: PartialSpellDto | null) => void, spellAction: PartialSpellDto) {
    const cleanupDelayInMs = 3500;
    const spellActionDescriptionTitle = isMyTurn
        ? "You used"
        : "Your opponent used";
    localStorage.setItem(
        localStorageKeys.playPage.spellActionDescription,
        spellActionDescriptionTitle
    );
    setActionSpell(spellAction);
    setTimeout(() => {
        setActionSpell(null);
    }, cleanupDelayInMs);
}

