import { createContext, useContext, useState } from "react";

const noError = "";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const HomeErrorContext = createContext({ error: noError, setHomeError: (_error: string) => { } })

interface HomeErrorContextProps {
    children?: React.ReactNode;
}

export default function HomeErrorContextProvider(props: HomeErrorContextProps) {
    const { children } = props;

    const [error, setHomeError] = useState<string>(noError);

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