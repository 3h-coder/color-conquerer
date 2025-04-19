import AppContexts from './AppContexts';
import AppRoutes from './routes/AppRoutes';

export default function App() {

  return (
    <AppContexts>
      <AppRoutes />
    </AppContexts>
  );
}
