import { useEffect, useRef } from "react";
import HomeButtons from "./components/HomeButtons";
import OpponentSearch from "./components/OpponentSearch";

export default function Home() {

    const contentWrapperRef = useRef<HTMLDivElement>(null);
    const homeButtonsRef = useRef<HTMLDivElement>(null);
    const opponentSearchRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const homeButtonsWidth = homeButtonsRef.current?.style.width;
        
        if (contentWrapperRef.current && homeButtonsWidth) {
            console.log("hey");
            contentWrapperRef.current.style.width = homeButtonsWidth;
          }
    }, []);

    return (
        <div className="home-container">
            <h1 className="main-title">Welcome to Color Conquerer</h1>
            <div className="content-wrapper" ref={contentWrapperRef}>
                <div className="content-container">
                    <HomeButtons ref={homeButtonsRef}/>
                    <OpponentSearch ref={opponentSearchRef}/>
                </div>
            </div> 
        </div>
    );
}