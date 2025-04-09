import { SwordIcon } from "../../../../../assets/svg";
import { cellStyle } from "../../../../../style/constants";
import { WithIconProps } from "../GameCellModifier";

export function SelectedIndicator() {
    return (
        <div className="selected-indicator" />
    );
}

export function AttackableIndicator(props: WithIconProps) {
    const { rotateIcon } = props;
    const rotateStyle = rotateIcon ? cellStyle.rotate180deg : undefined;

    return (
        <div className={`attackable-indicator ${cellStyle.classNames.absPosition}`}>
            <SwordIcon style={{ transform: rotateStyle }} />
        </div>
    );
}

export function SpellTargetIndicator() {
    return (
        <div className="possible-spell-target-indicator" />
    );
}