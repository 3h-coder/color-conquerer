interface SvgContainerProps {
    style?: React.CSSProperties;
    className?: string;
    children?: React.ReactNode;
}

export function SvgContainer(props: SvgContainerProps) {
    const { style, className, children } = props;

    return (
        <div className={`svg-container ${className}`} style={style}>
            {children}
        </div>
    );
}