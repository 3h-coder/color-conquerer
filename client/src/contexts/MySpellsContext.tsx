import { createContext, useContext, useState } from "react";
import { SpellDto } from "../dto/spell/SpellDto";

interface MySpellsContextObject {
    spells: SpellDto[];
    setSpells: React.Dispatch<React.SetStateAction<SpellDto[]>>;
}

const MySpellsContext = createContext<MySpellsContextObject>({
    spells: [],
    setSpells: () => { },
});

interface MySpellsContextProviderProps {
    children: React.ReactNode;
}

export default function MySpellsContextProvider(
    props: MySpellsContextProviderProps
) {
    const { children } = props;
    const [spells, setSpells] = useState<SpellDto[]>([]);

    return (
        <MySpellsContext.Provider value={{ spells, setSpells }}>
            {children}
        </MySpellsContext.Provider>
    );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useMySpells() {
    return useContext(MySpellsContext);
}
