export const colors = {
    idleCell: "white",
    opponentMasterCell: "red",
    ownMasterCell: "blue",
    ownCell: "rgb(79, 139, 242, 1)", // lighter blue,
    opponentCell: "rgb(247, 111, 111, 1)", // lighter red,
    ownCellMovementPossible: "rgb(176, 199, 248, 1)" // even lighter blue
}

export const cellStyle = {
    className : "cell",
    selectableClassName : "selectable",
    selectedClassName : "selected",
    hoveredClassName: "hovered",
}

export const animations = {
    grid: {
        cellAnimationTimeInMs: 500,
        cellAnimationDelayFactor: 3,
    }
}