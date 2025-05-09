import { useState } from "react";
import DoubleButtonModal from "../../../../components/modals/DoubleButtonModal";
import { useTurnContext } from "../../../../contexts/TurnContext";
import { Events } from "../../../../enums/events";
import { socket } from "../../../../env";

export default function ConcedeButton() {
    const { matchStarted } = useTurnContext();
    const [modalOpen, setModalOpen] = useState(false);

    const text = "Concede";
    const modalText = "Are you sure that you want to concede the game?";
    const firstButtonText = "Yes";
    const secondButtonText = "Cancel";

    function onClick() {
        setModalOpen(true);
    }

    function onCondeceConfirmed() {
        setModalOpen(false);
        socket.emit(Events.CLIENT_MATCH_CONCEDE);
    }

    function onCancel() {
        setModalOpen(false);
    }

    return (
        <>
            <button onClick={onClick} disabled={!matchStarted}>
                {text}
            </button>
            <DoubleButtonModal
                isOpenState={[modalOpen, setModalOpen]}
                firstButtonText={firstButtonText}
                secondButtonText={secondButtonText}
                firstButtonAction={onCondeceConfirmed}
                secondButtonAction={onCancel}
            >
                {modalText}
            </DoubleButtonModal>
        </>
    );
}
