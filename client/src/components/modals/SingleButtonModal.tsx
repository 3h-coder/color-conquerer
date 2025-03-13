import Modal, { ModalProps } from "./Modal";

interface SingleButtonModalProps extends ModalProps {
    buttonText: string;
    buttonAction?: () => unknown;
}

export default function SingleButtonModal(props: SingleButtonModalProps) {
    const {
        isOpenState,
        style,
        title,
        children,
        enableClosing,
        onClose,
        icon,
        buttonText,
        buttonAction,
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
                    // If the buttonAction is not defined, just call onClose
                    <button onClick={buttonAction === undefined ? onClose : buttonAction}>
                        {buttonText}
                    </button>
                )}
            </div>
        </Modal>
    );
}
