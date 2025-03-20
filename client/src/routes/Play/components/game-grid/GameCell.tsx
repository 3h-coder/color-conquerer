import { CellDto } from "../../../../dto/CellDto";
import { CellTransientState } from "../../../../enums/cellTransientState";
import { Events } from "../../../../enums/events";
import { EMPTY_STRING, socket, WHITE_SPACE } from "../../../../env";
import { cellStyle } from "../../../../style/constants";
import {
    canBeSpawnedOrMovedInto,
    getCellBackgroundColor,
    isSelectable
} from "../../../../utils/cellUtils";
import GameCellModifier from "./GameCellModifier";
import "./styles/GameCell.css";

interface GameCellProps {
    id: string;
    isPlayer1: boolean;
    cellInfo: CellDto;
    canInteract: boolean;
    canDisplayPossibleActions: boolean;
}

export default function GameCell(props: GameCellProps) {
    const { id, isPlayer1, cellInfo, canInteract, canDisplayPossibleActions } = props;

    const selectable = canInteract && isSelectable(cellInfo);
    const canBeSpellTargetted = cellInfo.transientState === CellTransientState.CAN_BE_SPELL_TARGETTED;

    function onCellClick() {
        if (!selectable) return;

        socket.emit(Events.CLIENT_CELL_CLICK, cellInfo);
    }

    const allClassNames = [
        selectable ? cellStyle.classNames.selectable : EMPTY_STRING,
        canDisplayPossibleActions && canBeSpawnedOrMovedInto(cellInfo)
            ? cellStyle.classNames.spawnOrMovePossible
            : EMPTY_STRING,
        canDisplayPossibleActions && canBeSpellTargetted
            ? cellStyle.classNames.possibleSpellTarget
            : EMPTY_STRING
    ];
    const classes = `${cellStyle.className} ${allClassNames.join(WHITE_SPACE)}`.trim();

    const computedBackgroundColor = getCellBackgroundColor(cellInfo, isPlayer1);

    return (
        <div
            className={classes}
            id={id}
            onClick={onCellClick}
            style={computedBackgroundColor}
        >
            <GameCellModifier cellInfo={cellInfo} isPlayer1={isPlayer1} />
        </div>
    );
}


