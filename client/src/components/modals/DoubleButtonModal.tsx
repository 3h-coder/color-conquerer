import Modal, { ModalProps } from "./Modal";

interface SingleButtonModalProps extends ModalProps {
    firstButtonText: string;
    firstButtonAction: () => unknown;
    secondButtonText: string;
    secondButtonAction: () => unknown;
}

export default function DoubleButtonModal(props: SingleButtonModalProps) {
    const {
        isOpenState,
        style,
        title,
        children,
        enableClosing,
        onClose,
        icon,
        firstButtonText,
        firstButtonAction,
        secondButtonText,
        secondButtonAction
    } = props;

    return (
        <Modal
            isOpenState={isOpenState}
            style={style}
            title={title}
            enableClosing={enableClosing}
            onClose={onClose}
            icon={icon}
        >
            {children}
            <div id="modal-footer">
                {enableClosing !== false && (
                    <>
                        <button onClick={firstButtonAction}>
                            {firstButtonText}
                        </button>
                        <button className="button-secondary" onClick={secondButtonAction}>
                            {secondButtonText}
                        </button>
                    </>
                )}
            </div>
        </Modal>
    );
}
