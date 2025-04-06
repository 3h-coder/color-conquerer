import { useEffect, useRef } from "react";
import { useMatchContext } from "../../../../contexts/MatchContext";
import { CellDto } from "../../../../dto/misc/CellDto";
import { CellStateUtils } from "../../../../enums/cellState";
import { CellTransientState } from "../../../../enums/cellTransientState";
import { Events } from "../../../../enums/events";
import { EMPTY_STRING, NEW_LINE, WHITE_SPACE } from "../../../../env";
import { cellStyle } from "../../../../style/constants";
import {
    AttachedCellBehavior,
    canBeSpawnedOrMovedInto,
    getCellBackgroundColor,
    isSelectable,
} from "../../../../utils/cellUtils";
import { bindTooltip, TooltipPosition } from "../../../../utils/tooltipUtils";
import GameCellModifier from "./GameCellModifier";
import "./styles/GameCell.css";

interface GameCellProps {
    id: string;
    isPlayer1: boolean;
    cellInfo: CellDto;
    canInteract: boolean;
    canDisplayEffects: boolean;
    attachedBehavior?: AttachedCellBehavior;
}

export default function GameCell(props: GameCellProps) {
    const { emit } = useMatchContext();
    const cellRef = useRef<HTMLDivElement>(null);

    const {
        id,
        isPlayer1,
        cellInfo,
        canInteract,
        canDisplayEffects,
        attachedBehavior
    } = props;

    const selectable = canInteract && isSelectable(cellInfo);
    const canBeSpellTargetted =
        cellInfo.transientState === CellTransientState.CAN_BE_SPELL_TARGETTED;

    const allClassNames = [
        selectable ? cellStyle.classNames.selectable : EMPTY_STRING,
        canDisplayEffects && canBeSpawnedOrMovedInto(cellInfo)
            ? cellStyle.classNames.spawnOrMovePossible
            : EMPTY_STRING,
        canDisplayEffects && canBeSpellTargetted
            ? cellStyle.classNames.possibleSpellTarget
            : EMPTY_STRING,
    ];
    const classes = `${cellStyle.className} ${allClassNames.join(WHITE_SPACE)}`.trim();
    const computedBackgroundColor = getCellBackgroundColor(cellInfo, isPlayer1);

    useEffect(() => {
        if (!cellRef.current) return;

        const tooltipText = CellStateUtils.getActiveStateDescriptions(cellInfo.state).join(`${NEW_LINE}${NEW_LINE}`);
        if (!tooltipText) return;

        const cleanup = bindTooltip(cellRef, {
            tooltipText: tooltipText,
            position: TooltipPosition.RIGHT,
        });

        return cleanup;
    }, [cellInfo]);

    function onCellClick() {
        if (!selectable) return;

        emit(Events.CLIENT_CELL_CLICK, cellInfo);
    }

    const onMouseEnter = attachedBehavior?.mouseEnter;
    const onMouseLeave = attachedBehavior?.mouseLeave;

    return (
        <div
            ref={cellRef}
            className={classes}
            id={id}
            style={computedBackgroundColor}
            onClick={onCellClick}
            onMouseEnter={onMouseEnter}
            onMouseLeave={onMouseLeave}
        >
            <GameCellModifier cellInfo={cellInfo} isPlayer1={isPlayer1} />
        </div>
    );
}
