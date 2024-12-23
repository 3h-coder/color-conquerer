export const colors = {
    cell: {
        idle: "white",
        opponentMaster: "red",
        ownMaster: "blue",
        own: "rgb(79, 139, 242, 1)", // lighter blue
        opponent: "rgb(247, 111, 111, 1)", // lighter red
        ownCellMovementPossible: "rgb(176, 199, 248, 1)"
    },
}

export const cellStyle = {
    className: "cell",
    selectableClassName: "selectable",
    selectedClassName: "selected",
    hoveredClassName: "hovered",
    possibleMoveClassName: "cell-possible-move"
}

export const animations = {
    grid: {
        cellAnimationTimeInMs: 500,
        cellAnimationDelayFactor: 3,
    }
}