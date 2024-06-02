import { SpinnerIcon } from "../assets/svg";
import { SvgContainer } from "./containers";

export default function LoadingSpinner() {

    return (
        <SvgContainer style={{animation: "rotate 2s infinite"}}>
            <SpinnerIcon style={{fill: "white"}}/>
        </SvgContainer>
    )
}