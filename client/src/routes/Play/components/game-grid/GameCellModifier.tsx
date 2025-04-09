import { CellDto } from "../../../../dto/misc/CellDto";
import { CellHiddenState } from "../../../../enums/cellHiddenState";
import { CellState, CellStateUtils } from "../../../../enums/cellState";
import { CellTransientState } from "../../../../enums/cellTransientState";
import { isOwnedAndCanBeSpellTargetted } from "../../../../utils/cellUtils";
import { Archer } from "./GameCellModifiers.tsx/Archer";
import { AttackableIndicator, SelectedIndicator, SpellTargetIndicator } from "./GameCellModifiers.tsx/Indicators";
import { LandMine } from "./GameCellModifiers.tsx/LandMine";
import { ManaBubble } from "./GameCellModifiers.tsx/ManaBubble";
import { Shield } from "./GameCellModifiers.tsx/Shield";
import { WindSpiral } from "./GameCellModifiers.tsx/WindSpiral";

interface GameCellModifierProps {
    cellInfo: CellDto;
    isPlayer1: boolean;
}

/**
 * Returns all the HTML elements that represent a cell modifier.
 */
export default function GameCellModifier(props: GameCellModifierProps) {
    const { cellInfo, isPlayer1 } = props;
    const containsState = CellStateUtils.contains;

    const selected = cellInfo.transientState === CellTransientState.SELECTED;
    const attackable =
        cellInfo.transientState === CellTransientState.CAN_BE_ATTACKED;
    const isManaBubble = containsState(
        cellInfo.state,
        CellState.MANA_BUBBLE
    );
    const isMineTrap = cellInfo.hiddenState == CellHiddenState.MINE_TRAP;
    const isShielded = containsState(
        cellInfo.state,
        CellState.SHIELDED
    );
    const isAccelerated = containsState(
        cellInfo.state,
        CellState.ACCELERATED
    );
    const isArcher = containsState(
        cellInfo.state,
        CellState.ARCHER
    );
    // If not owned, a background color is being applied to the cell instead
    const ownedAndCanBeSpellTargetted = isOwnedAndCanBeSpellTargetted(cellInfo);

    return (
        <>
            {selected && <SelectedIndicator />}
            {attackable && <AttackableIndicator rotateIcon={isPlayer1} />}
            {isManaBubble && <ManaBubble />}
            {isMineTrap && <LandMine rotateIcon={isPlayer1} isBlinking={false} />}
            {isShielded && <Shield />}
            {ownedAndCanBeSpellTargetted && <SpellTargetIndicator />}
            {isAccelerated && <WindSpiral />}
            {isArcher && <Archer rotateIcon={isPlayer1} />}
        </>
    );
}

export interface WithIconProps {
    rotateIcon: boolean;
}