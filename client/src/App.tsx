import UserContextProvider from './contexts/UserContext';
import AppRoutes from './routes/AppRoutes';

export default function App() {

  return (
    <UserContextProvider>
      <AppRoutes />
    </UserContextProvider>
  )
}
