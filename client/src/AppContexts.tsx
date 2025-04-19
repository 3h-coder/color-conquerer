import HomeErrorContextProvider from "./contexts/HomeErrorContext";
import UserContextProvider from "./contexts/UserContext";

interface AppContextsProps {
    children: React.ReactNode;
}

export default function AppContexts(props: AppContextsProps) {
    const { children } = props;

    return (
        <UserContextProvider>
            <HomeErrorContextProvider>
                {children}
            </HomeErrorContextProvider>
        </UserContextProvider>
    );
}