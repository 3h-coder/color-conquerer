import { useState } from "react";
import { ContainerProps } from "../../../../components/containers";
import SpawnButton from "./SpawnButton";
import SpellDeck from "./SpellDeck";
import SpellToggleButton from "./SpellToggleButton";
import "./styles/ActionBoard.css";

export default function ActionBoard() {
    const [spellsVisible, setSpellsVisible] = useState(false);

    return (
        <>
            <ActionBoardContainer>
                <SpawnButton />
                <SpellToggleButton spellsVisible={spellsVisible} setSpellsVisible={setSpellsVisible} />
            </ActionBoardContainer>
            {
                spellsVisible && (
                    <SpellDeck />
                )
            }
        </>
    );
}

function ActionBoardContainer(props: ContainerProps) {
    return (
        <div id="action-board-container">
            {props.children}
        </div>
    );
}



