import Modal, { ModalProps } from "./Modal";

interface CancelModalProps extends ModalProps { }

export default function CancelModal(props: CancelModalProps) {
    const { style, title, children, enableClosing, onClose } = props;

    return (
        <Modal style={style} title={title} enableClosing={enableClosing} onClose={onClose}>
            {children}
            <div className="modal-footer">
                {enableClosing !== false && <button onClick={props.onClose}>Cancel</button>}
            </div>
        </Modal>
    );
}