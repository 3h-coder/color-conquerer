import { ContainerProps } from "../../../../components/containers";
import SpawnButton from "../buttons/SpawnButton";

export default function ActionBoard() {
    return (
        <ActionBoardContainer>
            <SpawnButton />
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

