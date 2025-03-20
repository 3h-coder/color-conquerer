export const colors = {
    cell: {
        idle: "white",
        opponentMaster: "red",
        ownMaster: "blue",
        own: "rgb(79, 139, 242)", // lighter blue
        opponent: "rgb(247, 111, 111)", // lighter red
        movementOrSpawnPossible: "rgb(168, 213, 234)", // slightly lighter blue
        spellTargettingPossible: "rgb(248, 208, 239)",
        ownCellFreshlySpawned: "rgb(144, 183, 249)", // even lighter blue
        opponentCellFreshlySpawned: "rgb(249, 152, 152)", // even lighter red
    },
};

export const cellStyle = {
    className: "cell",
    rotate180deg: "rotate(180deg)",
    classNames: {
        selectable: "selectable",
        hovered: "hovered",
        spawnOrMovePossible: "spawn-or-move-possible",
        possibleSpellTarget: "possible-spell-target",
        absPosition: "absolute-positioning-centered"
    },
};