import { EMPTY_STRING } from "../env";

export interface ContainerProps {
    style?: React.CSSProperties;
    id?: string;
    className?: string;
    children?: React.ReactNode;
}

export function SvgContainer(props: ContainerProps) {
    const { style, className, id, children } = props;

    const extraClassStyle = className !== undefined ? ` ${className}` : EMPTY_STRING;

    return (
        <div className={`svg-container${extraClassStyle}`} style={style} id={id}>
            {children}
        </div>
    );
}

export function CenteredContainer(props: ContainerProps) {
    const { style, className, id, children } = props;

    const extraClassStyle = className !== undefined ? ` ${className}` : EMPTY_STRING;

    return (
        <div className={`centered-container${extraClassStyle}`} style={style} id={id}>
            {children}
        </div>
    );
}