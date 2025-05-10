import { LogoIcon } from "../../../assets/svg";
import { ContainerProps } from "../../../components/containers";

export default function LogoAndTitle() {
    const title = "Color Conquerer";

    return (
        <Logo>
            <h1>{title}</h1>
        </Logo>
    );
}

function Logo(props: ContainerProps) {
    return (
        <div id="logo-container">
            <LogoIcon />
            {props.children}
        </div>
    );
}