import Modal, { ModalProps } from "./Modal";

interface CancelModalProps extends ModalProps { }

export default function CancelModal(props: CancelModalProps) {
    const { style, title, children, onClose } = props;

    return (
        <Modal style={style} title={title} onClose={onClose}>
            {children}
            <div className="modal-footer">
                <button onClick={props.onClose}>Cancel</button>
            </div>
        </Modal>
    );
}