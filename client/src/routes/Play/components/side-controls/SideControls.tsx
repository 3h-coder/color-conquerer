import SideControlsContent from "./SideControlsContent";
import "./styles/SideControls.css";

export default function SideControls() {

    return (
        <div id="side-controls-container-outer">
            <div id="side-controls-container-inner">
                <SideControlsContent />
            </div>
        </div>

    );
}