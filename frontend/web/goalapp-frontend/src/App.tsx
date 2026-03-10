import { Route, Routes } from 'react-router'
import './App.css'
import DashboardPage from './features/main/pages/DashboardPage'
import PublicDashboardPage from './features/main/pages/PublicDashboardPage'
import LoginPage from './features/auth/pages/LoginPage'
import RegisterPage from './features/auth/pages/RegisterPage'
import FormComunication from './features/main/pages/FormComunication'
import SendEmailForgottenPasswd from './features/auth/pages/SendEmailForgottenPasswd'

function App() {

  return (
    <>
      <Routes>
        <Route path='/' element={<PublicDashboardPage />} />
        <Route path='/dashboard' element={<DashboardPage />} />
        <Route path='/comunication_form' element={<FormComunication />} />
        <Route path='/login' element={<LoginPage />} />
        <Route path='/register' element={<RegisterPage />} />
        <Route path='/send-email' element={<SendEmailForgottenPasswd />} />
      </Routes>
    </>
  )
}

export default App
