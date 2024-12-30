import { createContext, useContext, useEffect, useState } from "react";
import { HomeState } from "../enums/homeState";
import { HomeStateDto } from "../dto/HomeStateDto";
import { developmentErrorLog } from "../utils/loggingUtils";
import { ParseErrorDto } from "../dto/ErrorDto";
import { fetchHomeState } from "../api/home";
import { useUser } from "./UserContext";

const defaultHomeState: HomeStateDto = {
    state: HomeState.PLAY,
    topMessage: "",
    clearMatchSession: false
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const HomeStateContext = createContext({ homeState: defaultHomeState, setHomeState: (_state: HomeStateDto) => { }, loading: false })

interface HomeStateContextProps {
    children?: React.ReactNode;
}

export default function HomeStateContextProvider(props: HomeStateContextProps) {
    const { children } = props;
    const { user } = useUser();
    const [homeState, setHomeState] = useState<HomeStateDto>(defaultHomeState);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);

        if (user.isAuthenticating)
            return;
        setHomeStateContext();
    }, [user.isAuthenticating]);

    async function setHomeStateContext() {
        try {
            const fetchedHomeState = await fetchHomeState();
            setHomeState(fetchedHomeState);
        } catch (error: unknown) {
            developmentErrorLog("Failed to retrieve the home state", ParseErrorDto(error));
            setHomeState(defaultHomeState);
        } finally {
            setLoading(false);
        }
    }

    return (
        <HomeStateContext.Provider value={{ homeState, setHomeState, loading }}>
            {children}
        </HomeStateContext.Provider>
    );
}

export function useHomeState() {
    return useContext(HomeStateContext);
}