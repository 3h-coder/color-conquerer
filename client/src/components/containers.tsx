interface SvgContainerProps {
    style?: React.CSSProperties;
    children?: React.ReactNode;
}

export function SvgContainer(props: SvgContainerProps) {
    const { style, children } = props;

    return (
        <div className="svg-container" style={style}>
            {children}
        </div>
    );
}