import { useEffect, useState } from "react";
import { getCellId } from "../../../../utils/cellUtils";
import { delay } from "../../../../utils/domUtils";
import GameCell from "../../../Play/components/game-grid/GameCell";
import { GridInner, GridOuter, GridRow } from "../../../Play/components/game-grid/GameGrid";
import { animationActionsSequence } from "./animations/actionAnimations";
import { getDefaultGameGrid } from "./fakeGameGridSetupUtils";
import { FakeGameGridSetup } from "./Setups/FakeGameGridSetup";

export interface FakeGameGridProps {
    setup: FakeGameGridSetup;
}

export default function FakeGameGrid(props: FakeGameGridProps) {
    const { setup } = props;
    const [key, setKey] = useState(0);
    const forceRemount = () => setKey(prevKey => prevKey + 1);
    const boardArray = getDefaultGameGrid(setup.coordinatesSetup);
    const gridStyle: React.CSSProperties = {
        gridTemplateColumns: `repeat(${boardArray.length}, 1fr)`
    };
    const cellSize = "max(15px, 3vmin)";
    const cellStyle: React.CSSProperties = {
        width: cellSize,
        height: cellSize
    };

    useEffect(() => {
        animateSetup();

        async function animateSetup() {
            const allAttacks = setup.actionsSetup;
            const delayBetweenEachAttackInMs = 500;
            const wrappingDelayInMs = 1000;
            await delay(wrappingDelayInMs);
            await animationActionsSequence(allAttacks, delayBetweenEachAttackInMs);
            await delay(wrappingDelayInMs);
            forceRemount();
        }
    });

    return (
        <GridOuter key={key}>
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
                                style={cellStyle}
                            />
                        ))}
                    </GridRow>
                ))}
            </GridInner>
        </GridOuter>
    );
}

