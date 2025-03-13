import { useState } from "react";
import DoubleButtonModal from "../../../../components/modals/DoubleButtonModal";

export default function ConcedeButton() {
    const [modalOpen, setModalOpen] = useState(false);

    const text = "Concede";
    const modalText = "Are you sure that you want to concede the game?";
    const firstButtonText = "Yes";
    const secondButtonText = "Cancel";

    function onClick() {
        setModalOpen(true);
    }

    function onCondeceConfirmed() {
        // Nothing for now
    }

    function onCancel() {
        setModalOpen(false);
    }

    return (
        <>
            <button onClick={onClick}>
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
