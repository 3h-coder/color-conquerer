import { BombIcon, ShieldIcon } from "../../../assets/svg";
import { SpellId } from "../../../enums/spellId";

export function getSpellIcon(spellId: number): JSX.Element {
    switch (spellId) {
        case SpellId.MINE_TRAP:
            return <BombIcon />;

        case SpellId.SHIELD_FORMATION:
            return <ShieldIcon />;

        default:
            return <></>;
    }
}