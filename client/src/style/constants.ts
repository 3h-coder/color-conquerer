export const colors = {
    cell: {
        idle: "white",
        opponentMaster: "red",
        ownMaster: "blue",
        own: "rgb(79, 139, 242, 1)", // lighter blue
        opponent: "rgb(247, 111, 111, 1)", // lighter red
        ownCellActionPossible: "rgb(168, 213, 234, 1)", // slightly lighter blue
        ownCellFreshlySpawned: "rgb(144, 183, 249, 1)", // even lighter blue
        opponentCellFreshlySpawned: "rgb(249, 152, 152, 1)", // even lighter red
    },
};

export const cellStyle = {
    className: "cell",
    classNames: {
        selectable: "selectable",
        hovered: "hovered",
        possibleAction: "possible-action",
        absPosition: "absolute-positioning-centered"
    },
};