import { TfiCup } from "react-icons/tfi";
import { Link } from "react-router";

export default function Header() {
    return (
        <>
        <header className="bg-zinc-900 h-16 flex flex-row justify-between items-center sm:border-b border-gray-700 px-3 sm:px-0">
            <Link to={'/'} className="flex flex-row items-center justify-center gap-2 sm:w-1/3">
                <div className="bg-lime-300 p-2 rounded-md">
                    <TfiCup />
                </div>
                <p className="text-white font-bold">GoalApp</p>
            </Link>
            <div className="hidden sm:flex flex-row justify-center items-center gap-3 lg:gap-10 w-1/3">
                <a href="#" className="text-gray-400 text-sm hover:text-lime-300">Ligas</a>
                <a href="#" className="text-gray-400 text-sm hover:text-lime-300">Resultados</a>
                <a href="#" className="text-gray-400 text-sm hover:text-lime-300">Calendario</a>
                <a href="#" className="text-gray-400 text-sm hover:text-lime-300">Ranking</a>
            </div>
            <div className="flex flex-row justify-center items-center gap-3 lg:gap-5 sm:w-1/3">
                <Link to={'/login'} className="text-gray-400 text-sm">Login</Link>
                <Link to={'/register'} className="bg-lime-300 px-2 py-1 rounded-md text-zinc-900 text-sm">Registro</Link>
            </div>
        </header>
        <header className="bg-zinc-900 h-16 flex flex-row justify-between sm:hidden items-center border-b border-gray-700">
            <div className="flex flex-row justify-center items-center gap-3 sm:gap-10 lg:gap-10 w-full">
                <a href="#" className="text-gray-400 text-sm hover:text-lime-300">Ligas</a>
                <a href="#" className="text-gray-400 text-sm hover:text-lime-300">Resultados</a>
                <a href="#" className="text-gray-400 text-sm hover:text-lime-300">Calendario</a>
                <a href="#" className="text-gray-400 text-sm hover:text-lime-300">Ranking</a>
            </div>
        </header>
        </>
    )
}