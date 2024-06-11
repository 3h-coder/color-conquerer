/* eslint-disable react-refresh/only-export-components */
import { ReactNode, createContext, useContext, useState } from "react";
import UserDto from "../dto/UserDto";


export const guestUser: UserDto = {
    username: "guest"
};


// eslint-disable-next-line @typescript-eslint/no-unused-vars
const UserContext = createContext({ user: guestUser, setUser: (_user: UserDto) => { } });

interface UserContextProviderProps {
    children?: ReactNode;
}

export default function UserContextProvider(props: UserContextProviderProps) {
    const { children } = props;
    const [user, setUser] = useState<UserDto>(guestUser);

    return (
        <UserContext.Provider value={{ user, setUser }}>
            {children}
        </UserContext.Provider>
    );
}

export function useUser() {
    return useContext(UserContext);
}