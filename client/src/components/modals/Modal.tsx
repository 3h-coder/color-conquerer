import React from "react";
import ReactDOM from "react-dom";
import { BugIcon, InfoIcon, WarningTriangleIcon, XMarkIcon } from "../../assets/svg";
import { ModalIcon } from "../../enums/modalIcons";
import { getOrCreateDomElement } from "../../utils/domUtils";
import { SvgContainer } from "../containers";

export interface ModalProps {
    isOpenState: [boolean, React.Dispatch<React.SetStateAction<boolean>>];
    style?: React.CSSProperties;
    title?: string;
    children?: React.ReactNode;
    enableClosing?: boolean;
    onClose?: () => unknown;
    icon?: ModalIcon;
}

export default function Modal(props: ModalProps) {
    const { isOpenState, style, title, children, enableClosing, onClose, icon } = props;
    const [isOpen, setIsOpen] = isOpenState;

    function closeModal() {
        setIsOpen(false);
        if (onClose !== undefined)
            onClose();
    }

    return ReactDOM.createPortal(
        isOpen && (
            <div id="modal-overlay">
                <div id="modal-container" style={style}>
                    <div id="modal-header">
                        <Icon icon={icon ?? ModalIcon.None} />
                        <h2 style={{ margin: 0 }}>{title}</h2>
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
    let crossButtonDimensions = "max(25px, 3vmin)";

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
            crossButtonDimensions = "0";
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
    return getOrCreateDomElement("modal-root");
}