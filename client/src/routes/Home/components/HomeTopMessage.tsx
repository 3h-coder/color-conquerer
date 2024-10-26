import { useEffect, useState } from "react";
import { WarningTriangleIcon, XMarkIcon } from "../../../assets/svg";
import { SvgContainer } from "../../../components/containers";
import { useHomeState } from "../../../contexts/HomeStateContext";
import { HomeState } from "../../../enums/homeState";


export default function HomeTopMessage() {
    const { homeState } = useHomeState();
    const [display, setDisplay] = useState(homeState.topMessage !== "" && homeState.topMessage !== undefined);
    const [icon, setIcon] = useState<JSX.Element | undefined>(undefined);

    useEffect(() => {
        if (homeState.state === HomeState.JOIN_BACK)
            setIcon(<WarningTriangleIcon />);
    }, []);

    function onClose() {
        setDisplay(false);
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
            <span className="home-top-message-text">{homeState.topMessage}</span>
        </div>
    );
}