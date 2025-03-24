import { useState } from 'react';

export function useCellEffectSync() {
    const [canDisplayCellEffects, setCanDisplayCellEffects] = useState(true);

    function triggerCellEffectSync() {
        setCanDisplayCellEffects(false);
        setTimeout(() => setCanDisplayCellEffects(true), 100); // Force a reflow
    }

    return {
        canDisplayCellEffects,
        triggerCellEffectSync
    };
}