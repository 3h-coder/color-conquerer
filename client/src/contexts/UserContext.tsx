/* eslint-disable react-refresh/only-export-components */
import { ReactNode, createContext, useContext, useEffect, useState } from "react";
import { initSession } from "../api/session";
import UserDto from "../dto/UserDto";


export const guestUser: UserDto = {
    id: "undefined",
    username: "guest",
    isAuthenticating: true,
    isAuthenticated: false
};


// eslint-disable-next-line @typescript-eslint/no-unused-vars
const UserContext = createContext({ user: guestUser, setUser: (_user: UserDto) => { } });

interface UserContextProviderProps {
    children?: ReactNode;
}

export default function UserContextProvider(props: UserContextProviderProps) {
    const { children } = props;
    const [user, setUser] = useState<UserDto>(guestUser);

    useEffect(() => {
        initiateSession();

        // TODO: Change that when implementing user accounts
        setUser({ ...guestUser, isAuthenticating: false });
    }, []);

    async function initiateSession() {
        await initSession();
    }

    return (
        <UserContext.Provider value={{ user, setUser }}>
            {children}
        </UserContext.Provider>
    );
}

export function useUser() {
    return useContext(UserContext);
}