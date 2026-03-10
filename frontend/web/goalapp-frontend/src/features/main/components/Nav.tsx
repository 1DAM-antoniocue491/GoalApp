import { TfiCup } from "react-icons/tfi";
import { Link } from "react-router";
import { FaSearch } from "react-icons/fa";
import { IoIosNotificationsOutline } from "react-icons/io";

export default function Nav() {
    return (
        <>
        <div className="bg-zinc-800 flex flex-row justify-between items-center h-12">
            <Link to={'/'} className="flex flex-row items-center justify-center gap-2 sm:w-1/3">
                <div className="bg-lime-300 p-2 rounded-md">
                    <TfiCup />
                </div>
                <p className="text-white font-bold">GoalApp</p>
            </Link>
            <div className="flex flex-row items-center gap-2">
                <Link to={''}>
                    <div className="bg-lime-300/15 rounded-lg px-3">
                        <p className="text-lime-300 py-1 border-b-2 font-semibold text-sm">Inicio</p>
                    </div>
                </Link>

                <Link to={''}>
                    <div className="px-3">
                        <p className="text-zinc-500 py-1 font-semibold text-sm">Ligas</p>
                    </div>
                </Link>

                <Link to={''}>
                    <div className="px-3">
                        <p className="text-zinc-500 py-1 font-semibold text-sm">Equipos</p>
                    </div>
                </Link>

                <Link to={''}>
                    <div className="px-3">
                        <p className="text-zinc-500 py-1 font-semibold text-sm">Estadísticas</p>
                    </div>
                </Link>
            </div>

            <div className="flex flex-row items-center">
                <div className="p-2 rounded-full bg-zinc-700 border border-zinc-600">
                    <FaSearch className="text-zinc-500 w-3 h-3"/>
                </div>

                <div className="relative p-1.5 rounded-full bg-zinc-700 border border-zinc-600">
                    <IoIosNotificationsOutline className="text-zinc-500" />
                    
                    <div className="absolute top-0 right-0 w-2.5 h-2.5 bg-lime-300 rounded-full border-2 border-zinc-700"></div>
                </div>
            </div>
        </div>
        </>
    )
}