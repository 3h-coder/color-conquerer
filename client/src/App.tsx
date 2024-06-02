import  UserContextProvider from './contexts/UserContext';
import AppRoutes from './routes/AppRoutes';
import './style/css/App.css';

export default function App() {

  return (
    <UserContextProvider>
      <AppRoutes />
    </UserContextProvider>
  )
}
