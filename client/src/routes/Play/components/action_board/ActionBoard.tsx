import { useState } from "react";
import { ContainerProps } from "../../../../components/containers";
import SpawnButton from "../buttons/SpawnButton";
import SpellToggleButton from "../buttons/SpellToggleButton";
import SpellDeck from "./SpellDeck";

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
        <div className="action-board-container">
            {props.children}
        </div>
    );
}



