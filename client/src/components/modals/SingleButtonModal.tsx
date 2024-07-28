import Modal, { ModalProps } from "./Modal";

interface SingleButtonModalProps extends ModalProps {
    buttonText: string;
    buttonAction?: () => unknown;
}

export default function SingleButtonModal(props: SingleButtonModalProps) {
    const { style, title, children, enableClosing, onClose, buttonText, buttonAction } = props;

    return (
        <Modal style={style} title={title} enableClosing={enableClosing} onClose={onClose}>
            {children}
            <div className="modal-footer">
                {enableClosing !== false && <button onClick={buttonAction === undefined ? onClose : buttonAction}>{buttonText}</button>}
            </div>
        </Modal>
    );
}