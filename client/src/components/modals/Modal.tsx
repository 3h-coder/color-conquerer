import React, { useState } from "react";
import ReactDOM from "react-dom";
import { BugIcon, InfoIcon, WarningTriangleIcon, XMarkIcon } from "../../assets/svg";
import { ModalIcon } from "../../enums/modalIcons";
import { SvgContainer } from "../containers";
import { HTMLElements } from "../../env";

export interface ModalProps {
    style?: React.CSSProperties;
    title?: string;
    children?: React.ReactNode;
    enableClosing?: boolean;
    onClose?: () => unknown;
    icon?: ModalIcon;
}

export default function Modal(props: ModalProps) {
    const { style, title, children, enableClosing, onClose, icon } = props;
    const [isOpen, setIsOpen] = useState(true);

    function closeModal() {
        if (onClose !== undefined)
            onClose();

        setIsOpen(false);
    }

    return ReactDOM.createPortal(
        isOpen && (
            <div className="modal-overlay">
                <div className="modal-container" style={style}>
                    <div className="modal-header">
                        <Icon icon={icon ?? ModalIcon.None} />
                        <h4 style={{ margin: 0 }}>{title}</h4>
                        {enableClosing !== false && <CloseButton onClick={closeModal} />}
                    </div>
                    {children}
                </div>
            </div>),
        getModalRoot()
    );

}

interface IconProps {
    icon: ModalIcon;
}

function Icon(props: IconProps) {
    const { icon } = props;
    const crossButtonDimensions = "max(25px, 3vmin)";

    let actualIcon: JSX.Element;
    switch (icon) {
        case ModalIcon.Info:
            actualIcon = <InfoIcon />;
            break;

        case ModalIcon.Warning:
            actualIcon = <WarningTriangleIcon />;
            break;

        case ModalIcon.Error:
            actualIcon = <BugIcon />;
            break;

        default:
            actualIcon = <></>;
            break;
    }

    return (
        <SvgContainer style={{
            width: crossButtonDimensions,
            height: crossButtonDimensions,
        }}>
            {actualIcon}
        </SvgContainer>
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
    );
}

function getModalRoot() {
    const modalRootId = "modal-root";
    let modalRoot = document.getElementById(modalRootId);
    if (!modalRoot) {
        modalRoot = document.createElement(HTMLElements.div);
        modalRoot.id = modalRootId;
        document.body.appendChild(modalRoot);
    }
    return modalRoot;
}