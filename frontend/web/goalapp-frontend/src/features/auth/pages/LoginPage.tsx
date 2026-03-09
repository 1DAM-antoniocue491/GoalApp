import { Link } from "react-router";

export default function LoginPage() {
    return (
        <>
        <div className="bg-zinc-950 h-screen flex justify-center items-center">
            <div className="bg-zinc-900">
                <p>GoalApp</p>
                <h2>Bienvenido</h2>

                <div>
                    <Link to={'/login'}>Iniciar Sesión</Link>
                    <Link to={'/register'}>Registrarse</Link>
                </div>

                <form action=""></form>

            </div>
        </div>
        </>
    )
}