import React, { useState } from "react";
import ReactDOM from "react-dom";
import { XMarkIcon } from "../../assets/svg";
import { SvgContainer } from "../containers";

export interface ModalProps {
    style?: React.CSSProperties;
    title?: string;
    children?: React.ReactNode;
    enableClosing?: boolean;
    onClose?: () => unknown;
}

export default function Modal(props: ModalProps) {
    const { style, title, children, enableClosing, onClose } = props;
    const [isOpen, setIsOpen] = useState(true);

    function closeModal() {
        if (onClose !== undefined) {
            onClose();
        }
        setIsOpen(false);
    }

    return ReactDOM.createPortal(
        isOpen && (
            <div className="modal-overlay">
                <div className="modal-container" style={style}>
                    <div className="modal-header">
                        <h4 style={{ margin: 0 }}>{title}</h4>
                        {enableClosing !== false && <CloseButton onClick={closeModal} />}
                    </div>
                    {children}
                </div>
            </div>),
        getModalRoot()
    );

}

interface CloseButtonProps {
    onClick: () => unknown;
}

function CloseButton(props: CloseButtonProps) {
    const { onClick } = props;
    const crossButtonDimensions = "max(15px, 2vmin)";

    return (
        <button className="transparent no-border fit-content"
            onClick={onClick}>
            <SvgContainer style={{
                width: crossButtonDimensions,
                height: crossButtonDimensions,
            }}>
                <XMarkIcon />
            </SvgContainer>
        </button>
    )
}

function getModalRoot() {
    let modalRoot = document.getElementById('modal-root');
    if (!modalRoot) {
        modalRoot = document.createElement('div');
        modalRoot.id = 'modal-root';
        document.body.appendChild(modalRoot);
    }
    return modalRoot;
}