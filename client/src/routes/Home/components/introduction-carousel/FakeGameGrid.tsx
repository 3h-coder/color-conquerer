import { useEffect, useState } from "react";
import { useSliderContext } from "../../../../components/slider/SliderContext";
import { cellStyle } from "../../../../style/constants";
import { getCellId } from "../../../../utils/cellUtils";
import { delay } from "../../../../utils/domUtils";
import { BoolRef } from "../../../../utils/typeAliases";
import GameCell from "../../../Play/components/game-grid/GameCell";
import { GridInner, GridOuter, GridRow } from "../../../Play/components/game-grid/GameGrid";
import { animationActionsSequence } from "./animations/actionAnimations";
import { getDefaultGameGrid } from "./fakeGameGridSetupUtils";
import { FakeGameGridSetup } from "./Setups/FakeGameGridSetup";

export interface FakeGameGridProps {
    gridId: string;
    index: number;
    setup: FakeGameGridSetup;
}

export default function FakeGameGrid(props: FakeGameGridProps) {
    const { gridId, index, setup } = props;
    const { nextOrPreviousSlide, currentSlideIndex } = useSliderContext();
    const inFrame = index === currentSlideIndex;

    const [key, setKey] = useState(0);
    const forceRemount = () => setKey(prevKey => prevKey + 1);

    const boardArray = getDefaultGameGrid(setup.coordinatesSetup);
    const gridStyle: React.CSSProperties = {
        transform: cellStyle.rotate180deg,
        gridTemplateColumns: `repeat(${boardArray.length}, 1fr)`
    };
    const cellSize = "max(20px, 3vmin)";
    const cellDimensions: React.CSSProperties = {
        width: cellSize,
        height: cellSize
    };

    useEffect(() => {
        const isCancelledRef: BoolRef = { value: false };

        if (inFrame)
            animateSetup();

        async function animateSetup() {
            const allAttacks = setup.actionsSetup;
            const delayBetweenEachAttackInMs = 500;
            const wrappingDelayInMs = 1000;

            await delay(wrappingDelayInMs);
            if (isCancelledRef.value)
                return;

            await animationActionsSequence(allAttacks, delayBetweenEachAttackInMs, gridId, isCancelledRef);
            if (isCancelledRef.value)
                return;

            await delay(wrappingDelayInMs);
            if (isCancelledRef.value)
                return;

            nextOrPreviousSlide();

            await delay(wrappingDelayInMs);
            forceRemount();
        }

        return () => {
            isCancelledRef.value = true;
        };
    }, [inFrame]);

    return (
        <GridOuter key={key} id={gridId}>
            <GridInner style={gridStyle}>
                {boardArray.map((row, rowIndex) => (
                    <GridRow className="row" id={`r-${rowIndex}`} key={rowIndex}>
                        {row.map((cellInfo, colIndex) => (
                            <GameCell
                                key={colIndex}
                                id={getCellId(rowIndex, colIndex)}
                                isPlayer1={true}
                                cellInfo={cellInfo}
                                canInteract={false}
                                canDisplayEffects={false}
                                attachedBehavior={undefined}
                                style={cellDimensions}
                            />
                        ))}
                    </GridRow>
                ))}
            </GridInner>
        </GridOuter>
    );
}

