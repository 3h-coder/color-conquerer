import { BombIcon, BowArrowIcon, CrossingSwordsIcon, ShieldIcon, WindIcon } from "../../../assets/svg";
import { SpellId } from "../../../enums/spellId";

export function getSpellIcon(spellId: number): JSX.Element {
    const spellIcons: Record<number, JSX.Element> = {
        [SpellId.MINE_TRAP]: <BombIcon />,
        [SpellId.SHIELD_FORMATION]: <ShieldIcon />,
        [SpellId.CELERITY]: <WindIcon />,
        [SpellId.ARCHERY_VOW]: <BowArrowIcon />,
        [SpellId.AMBUSH]: <CrossingSwordsIcon />,
    };

    return spellIcons[spellId] || <></>;
}