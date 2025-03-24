import { useState } from "react";
import { create2DArray } from "../../../../../utils/arrayUtils";
import { AttachedCellBehavior } from "../../../../../utils/cellUtils";


export function useAttachedCellBehaviors(boardSize: number) {
    const [attachedCellBehaviors, setAttachedCellBehaviors] = useState<(AttachedCellBehavior | undefined)[][]>(
        create2DArray<AttachedCellBehavior>(boardSize)
    );

    function cleanupAttachedCellBehaviors() {
        attachedCellBehaviors.forEach(row => {
            row.forEach(behavior => {
                if (behavior?.isActive)
                    behavior?.cleanup?.();
            });
        });
        setAttachedCellBehaviors(create2DArray<AttachedCellBehavior>(boardSize));
    }

    return {
        attachedCellBehaviors,
        setAttachedCellBehaviors,
        cleanupAttachedCellBehaviors
    };
}