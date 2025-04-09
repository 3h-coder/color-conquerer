import { BombIcon, BowArrowIcon, ShieldIcon, WindIcon } from "../../../assets/svg";
import { SpellId } from "../../../enums/spellId";

export function getSpellIcon(spellId: number): JSX.Element {
    switch (spellId) {
        case SpellId.MINE_TRAP:
            return <BombIcon />;

        case SpellId.SHIELD_FORMATION:
            return <ShieldIcon />;

        case SpellId.CELERITY:
            return <WindIcon />;

        case SpellId.ARCHERY_VOW:
            return <BowArrowIcon />;

        default:
            return <></>;
    }
}