import { createContext, useContext, useState } from "react";
import { EMPTY_STRING } from "../env";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const HomeErrorContext = createContext({ error: EMPTY_STRING, setHomeError: (_error: string) => { } })

interface HomeErrorContextProps {
    children?: React.ReactNode;
}

export default function HomeErrorContextProvider(props: HomeErrorContextProps) {
    const { children } = props;

    const [error, setHomeError] = useState<string>(EMPTY_STRING);

    return (
        <HomeErrorContext.Provider value={{ error, setHomeError }}>
            {children}
        </HomeErrorContext.Provider>
    )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useHomeError() {
    return useContext(HomeErrorContext);
}