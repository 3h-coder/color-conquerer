import { useEffect, useState } from "react";
import { checkIfInMatch } from "../../../api/session";
import { WarningTriangleIcon, XMarkIcon } from "../../../assets/svg";
import { SvgContainer } from "../../../components/containers";


export default function HomeTopMessage() {
    const [message, setMessage] = useState("You are currently in a match! Click on the button below to join it back.");
    const [display, setDisplay] = useState(true);
    const [icon, setIcon] = useState<JSX.Element | undefined>(<WarningTriangleIcon />);

    useEffect(() => {
        fetchMessageToDisplay();
    }, [])

    async function fetchMessageToDisplay() {
        const isInMatch = (await checkIfInMatch()).value
        if (isInMatch) {
            setDisplay(true);
            setMessage("You are currently in a match");
            setIcon(<WarningTriangleIcon />);
        }
    }

    function onClose() {
        setDisplay(false);
        setMessage("");
    }

    const crossButtonDimensions = "max(15px, 2vmin)";
    const iconDimensions = "max(20px, 3vmin)";

    return (
        <div className="home-top-message-container" style={{ opacity: display ? 1 : 0, userSelect: display ? "text" : "none" }}>
            <div className="home-top-message-header">
                <SvgContainer style={{ width: iconDimensions, height: iconDimensions }}>
                    {icon !== undefined && icon}
                </SvgContainer>
                <button className="transparent no-border fit-content" onClick={onClose}>
                    <SvgContainer style={{ width: crossButtonDimensions, height: crossButtonDimensions }}>
                        <XMarkIcon />
                    </SvgContainer>
                </button>
            </div>
            <span className="home-top-message-text">{message}</span>
        </div>
    );
}