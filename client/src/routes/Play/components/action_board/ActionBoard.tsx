import { useState } from "react";
import { ContainerProps } from "../../../../components/containers";
import SpawnButton from "../buttons/SpawnButton";
import SpellToggleButton from "../buttons/SpellToggleButton";

export default function ActionBoard() {
    const [spellsVisible, setSpellsVisible] = useState(false);

    return (
        <ActionBoardContainer>
            <SpawnButton />
            <SpellToggleButton spellsVisible={spellsVisible} setSpellsVisible={setSpellsVisible} />
        </ActionBoardContainer>
    );
}

function ActionBoardContainer(props: ContainerProps) {
    return (
        <div className="action-board-container">
            {props.children}
        </div>
    );
}

