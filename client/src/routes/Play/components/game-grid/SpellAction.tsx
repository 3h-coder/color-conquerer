import { ContainerProps, Separator, SvgContainer } from "../../../../components/containers";

import { PartialSpellDto } from "../../../../dto/spell/PartialSpellDto";
import { localStorageKeys } from "../../../../env";
import { getSpellIcon } from "../shared";

interface SpellActionProps {
    spell: PartialSpellDto;
    setSpellAction: (spellAction: PartialSpellDto | null) => void;
}

export default function SpellAction(props: SpellActionProps) {
    const { spell, setSpellAction } = props;
    // We're not using extractKey as this component gets re-rendered when
    // the user selects a cell of their own
    const titleText = localStorage.getItem(localStorageKeys.playPage.spellActionDescriptionTitle);
    const iconSize = "1.2rem";

    return (
        <div id="action-spell-description-outer" onClick={() => setSpellAction(null)}>
            {titleText && <h3>{titleText}</h3>}
            <div id="action-spell-description-inner">
                <HeaderSection>
                    <SvgContainer style={{ width: iconSize, height: iconSize }}>
                        {getSpellIcon(spell.id)}
                    </SvgContainer>
                    {spell.name}
                </HeaderSection>
                <Separator style={{ marginBottom: "max(1vmin, 5px)" }} />
                {spell.description}
                <div className="spell-mana-cost">
                    {spell.manaCost}
                </div>
            </div>
        </div>
    );
}

function HeaderSection(props: ContainerProps) {
    const { children } = props;

    return (
        <div className="casted-spell-header">
            {children}
        </div>
    );
}

