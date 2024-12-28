export const colors = {
    cell: {
        idle: "white",
        opponentMaster: "red",
        ownMaster: "blue",
        own: "rgb(79, 139, 242, 1)", // lighter blue
        opponent: "rgb(247, 111, 111, 1)", // lighter red
        ownCellActionPossible: "rgb(176, 199, 248, 1)", // slightly lighter blue
        ownCellFreshlySpawned: "rgb(144, 183, 249, 1)", // even lighter blue
        opponentCellFreshlySpawned: "rgb(249, 152, 152, 1)", // even lighter red
    },
}

export const cellStyle = {
    className: "cell",
    selectableClassName: "selectable",
    selectedClassName: "selected",
    hoveredClassName: "hovered",
    absPositionClassName: "absolute-positioning-centered"
}

export const animations = {
    grid: {
        cellAnimationTimeInMs: 500,
        cellAnimationDelayFactor: 3,
    }
}