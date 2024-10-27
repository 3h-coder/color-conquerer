import { useEffect, useState } from "react";
import { InfoIcon, WarningTriangleIcon, XMarkIcon } from "../../../assets/svg";
import { SvgContainer } from "../../../components/containers";
import { useHomeState } from "../../../contexts/HomeStateContext";
import { HomeState } from "../../../enums/homeState";
import { clearMatchInfoFromSession } from "../../../api/session";


export default function HomeTopMessage() {
    const { homeState } = useHomeState();
    const [display, setDisplay] = useState(false);
    const [icon, setIcon] = useState<JSX.Element>(<InfoIcon />);

    useEffect(() => {
        if (Boolean(homeState.topMessage))
            setDisplay(true);

        if (homeState.state === HomeState.JOIN_BACK)
            setIcon(<WarningTriangleIcon />);

        if (homeState.clearMatchSession)
            clearMatchInfoFromSession();

    }, [homeState.state, homeState.clearMatchSession, homeState.topMessage]);

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