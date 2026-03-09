import React  from "react";
import { TfiCup } from "react-icons/tfi";
import { AiOutlineThunderbolt } from "react-icons/ai";
import { MdNavigateNext, MdOutlineSecurity, MdEmail } from "react-icons/md";
import { SiIndiansuperleague } from "react-icons/si";
import { TbPlayFootball } from "react-icons/tb";
import { CiCalendarDate } from "react-icons/ci";
import { PiRankingBold, PiCirclesFourBold } from "react-icons/pi";
import { FaPhoneAlt } from "react-icons/fa";
import { FaLocationDot } from "react-icons/fa6";
import { Link } from "react-router";

export default function PublicDashboardPage() {
    return (
        <>
        
        <header className="bg-zinc-900 h-16 flex flex-row justify-between items-center sm:border-b border-gray-700">
            <div className="flex flex-row items-center justify-center gap-2 w-1/3">
                <div className="bg-lime-300 p-2 rounded-md">
                    <TfiCup />
                </div>
                <p className="text-white font-bold">GoalApp</p>
            </div>
            <div className="hidden sm:flex flex-row justify-center items-center gap-3 lg:gap-10 w-1/3">
                <a href="#" className="text-gray-400 text-sm hover:text-lime-300">Ligas</a>
                <a href="#" className="text-gray-400 text-sm hover:text-lime-300">Resultados</a>
                <a href="#" className="text-gray-400 text-sm hover:text-lime-300">Calendario</a>
                <a href="#" className="text-gray-400 text-sm hover:text-lime-300">Ranking</a>
            </div>
            <div className="flex flex-row justify-center items-center gap-3 lg:gap-5 w-1/3">
                <Link to={'/login'} className="text-gray-400 text-sm">Login</Link>
                <Link to={'/register'} className="bg-lime-300 px-2 py-1 rounded-md text-zinc-900 text-sm">Registro</Link>
            </div>
        </header>
        <header className="bg-zinc-900 h-16 flex flex-row justify-between sm:hidden items-center border-b border-gray-700">
            <div className="flex flex-row justify-center items-center gap-10 lg:gap-10 w-full">
                <a href="#" className="text-gray-400 text-sm hover:text-lime-300">Ligas</a>
                <a href="#" className="text-gray-400 text-sm hover:text-lime-300">Resultados</a>
                <a href="#" className="text-gray-400 text-sm hover:text-lime-300">Calendario</a>
                <a href="#" className="text-gray-400 text-sm hover:text-lime-300">Ranking</a>
            </div>
        </header>

        <div className="gap-4 py-20 bg-gradient-to-br from-zinc-900 to-zinc-700 from-50% p-10 flex flex-col justify-center items-center">
            <div className="flex flex-row items-center justify-center gap-2 bg-zinc-700 px-3 py-1 rounded-full text-sm text-zinc-300 border border-lime-300">
                <AiOutlineThunderbolt className="text-lime-300" />
                <p>La mejor plataforma de gestión deportiva</p>
            </div>

            <div className="flex flex-col justify-center items-center">
                <h1 className="text-white text-3xl font-bold text-center">Gestiona tu Liga Deportiva de forma</h1>
                <h1 className="text-lime-300 text-3xl font-bold text-center">Profesional</h1>
            </div>

            <p className="text-sm text-zinc-500 sm:w-3/5 text-center">
                Una plataforma completa para organizar ligas, gestionar equipos
                seguir resultados y mantener actualizados los rankings en tiempo real.
            </p>

            <div className="flex flex-row gap-2">
                <Link to={'/register'} className="bg-lime-300 px-2 py-2 rounded-xl text-zinc-900 text-sm flex flex-row justify-center items-center font-semibold">
                    <p>Comenzar Ahora</p>
                    <MdNavigateNext />
                </Link>
                <Link to={'/login'} className="text-gray-300 border border-gray-400 text-sm py-2 px-5 rounded-xl font-semibold">Iniciar Sesión</Link>
            </div>
        </div>

        <div className="bg-zinc-900 flex flex-col items-center gap-2 pt-10 px-5 sm:px-0">
            <h3 className="text-xl text-white font-semibold">Todo lo que necesitas</h3>
            <p className="text-zinc-400 text-sm text-center">Herramientas profesionales para gestionar cada aspecto de tu liga deportiva</p>

            <div className="grid grid-cols-2 lg:grid-cols-4 pt-4 sm:p-7 gap-2">
                <div className="bg-zinc-800 flex flex-col justify-center items-center p-5 gap-2 rounded-lg">
                    <div className="bg-lime-300 p-2 rounded-md">
                        <SiIndiansuperleague />
                    </div>
                    <p className="text-white font-semibold">Gestión de Ligas</p>
                    <p className="text-zinc-500 text-sm text-center">Organiza y administra múltiples ligas deportivas desde una sola plataforma.</p>
                </div>

                <div className="bg-zinc-800 flex flex-col justify-center items-center p-5 gap-2 rounded-lg">
                    <div className="bg-lime-300 p-2 rounded-md">
                        <TbPlayFootball />
                    </div>
                    <p className="text-white font-semibold">Equipos & Jugadores</p>
                    <p className="text-zinc-500 text-sm text-center">Control completo de equipos, jugadores y estadísticas en tiempo real.</p>
                </div>

                <div className="bg-zinc-800 flex flex-col justify-center items-center p-5 gap-2 rounded-lg">
                    <div className="bg-lime-300 p-2 rounded-md">
                        <CiCalendarDate />
                    </div>
                    <p className="text-white font-semibold">Calendario Inteligente</p>
                    <p className="text-zinc-500 text-sm text-center">Programa partidos y eventos con un sistema de calendario automatizado.</p>
                </div>
                
                <div className="bg-zinc-800 flex flex-col justify-center items-center p-5 gap-2 rounded-lg">
                    <div className="bg-lime-300 p-2 rounded-md">
                        <PiRankingBold />
                    </div>
                    <p className="text-white font-semibold">Rankings Actualizados</p>
                    <p className="text-zinc-500 text-sm text-center">Tablas de posiciones y clasificaciones actualizadas automáticamente.</p>
                </div>
            </div>
        </div>

        <div className="bg-zinc-900 grid grid-cols-1 lg:grid-cols-2 justify-center p-10 lg:px-20 gap-5 lg:gap-20">
            <div>
                <div className="flex flex-row justify-between items-end">
                    <div className="flex flex-row items-center gap-1">
                        <PiCirclesFourBold className="text-lime-300 w-4 h-4"/>
                        <p className="text-white font-semibold">Resultados Recientes</p>
                    </div>
                    <a href="#" className="text-cyan-600 text-sm hover:underline">Ver todos</a>
                </div>
                <div className="flex flex-col gap-2 mt-3">
                    <div className="bg-zinc-800 p-3 rounded-lg flex flex-col gap-2">
                        <div className="flex flex-row justify-between items-center">
                            <p className="text-zinc-300 text-sm">Real Madrid</p>
                            <p className="text-white font-bold">3</p>
                        </div>
                        <div className="flex flex-row justify-between items-center">
                            <p className="text-zinc-300 text-sm">Barcelona</p>
                            <p className="text-white font-bold">1</p>
                        </div>
                        <div className="w-full border border-zinc-700" />
                        <p className="text-zinc-600 font-semibold text-sm">Liga Premier</p>
                    </div>
                    <div className="bg-zinc-800 p-3 rounded-lg flex flex-col gap-2">
                        <div className="flex flex-row justify-between items-center">
                            <p className="text-zinc-300 text-sm">Real Madrid</p>
                            <p className="text-white font-bold">3</p>
                        </div>
                        <div className="flex flex-row justify-between items-center">
                            <p className="text-zinc-300 text-sm">Barcelona</p>
                            <p className="text-white font-bold">1</p>
                        </div>
                        <div className="w-full border border-zinc-700" />
                        <p className="text-zinc-600 font-semibold text-sm">Liga Premier</p>
                    </div>
                    <div className="bg-zinc-800 p-3 rounded-lg flex flex-col gap-2">
                        <div className="flex flex-row justify-between items-center">
                            <p className="text-zinc-300 text-sm">Real Madrid</p>
                            <p className="text-white font-bold">3</p>
                        </div>
                        <div className="flex flex-row justify-between items-center">
                            <p className="text-zinc-300 text-sm">Barcelona</p>
                            <p className="text-white font-bold">1</p>
                        </div>
                        <div className="w-full border border-zinc-700" />
                        <p className="text-zinc-600 font-semibold text-sm">Liga Premier</p>
                    </div>
                </div>
            </div>
            <div>
                <div className="flex flex-row justify-between items-end">
                    <div className="flex flex-row items-center gap-1">
                        <PiCirclesFourBold className="text-lime-300 w-4 h-4"/>
                        <p className="text-white font-semibold">Próximos Partidos</p>
                    </div>
                    <a href="#" className="text-cyan-600 text-sm hover:underline">Ver todos</a>
                </div>
                <div className="flex flex-col gap-2 mt-3">
                    <div className="bg-zinc-800 p-3 rounded-lg flex flex-col gap-2">
                        <div>
                            <div className="flex flex-row justify-between items-center">
                                <p className="text-zinc-300 text-sm">Liverpool</p>
                                <p className="text-lime-300 font-semibold text-sm">28 Feb</p>
                            </div>
                            <div className="flex flex-row justify-between items-center">
                                <p className="text-zinc-300 text-sm">Chelsea</p>
                                <p className="text-zinc-500 font-semibold text-sm">15:00</p>
                            </div>
                        </div>
                        <div className="w-full border border-zinc-700" />
                        <p className="text-zinc-600 font-semibold text-sm">Liga Premier</p>
                    </div>
                    <div className="bg-zinc-800 p-3 rounded-lg flex flex-col gap-2">
                        <div>
                            <div className="flex flex-row justify-between items-center">
                                <p className="text-zinc-300 text-sm">Liverpool</p>
                                <p className="text-lime-300 font-semibold text-sm">28 Feb</p>
                            </div>
                            <div className="flex flex-row justify-between items-center">
                                <p className="text-zinc-300 text-sm">Chelsea</p>
                                <p className="text-zinc-500 font-semibold text-sm">15:00</p>
                            </div>
                        </div>
                        <div className="w-full border border-zinc-700" />
                        <p className="text-zinc-600 font-semibold text-sm">Liga Premier</p>
                    </div>
                    <div className="bg-zinc-800 p-3 rounded-lg flex flex-col gap-2">
                        <div>
                            <div className="flex flex-row justify-between items-center">
                                <p className="text-zinc-300 text-sm">Liverpool</p>
                                <p className="text-lime-300 font-semibold text-sm">28 Feb</p>
                            </div>
                            <div className="flex flex-row justify-between items-center">
                                <p className="text-zinc-300 text-sm">Chelsea</p>
                                <p className="text-zinc-500 font-semibold text-sm">15:00</p>
                            </div>
                        </div>
                        <div className="w-full border border-zinc-700" />
                        <p className="text-zinc-600 font-semibold text-sm">Liga Premier</p>
                    </div>
                </div>
            </div>
        </div>

        <div className="bg-zinc-800 px-5 sm:px-20 lg:px-80 py-10 flex flex-col ga">
            <div className="flex flex-row justify-between items-end">
                <div className="flex flex-row items-center gap-1">
                    <PiCirclesFourBold className="text-lime-300 w-4 h-4"/>
                    <p className="text-white font-semibold">Próximos Partidos</p>
                </div>
                <a href="#" className="text-cyan-600 text-sm hover:underline">Ver completa</a>
            </div>
            <div className="shadow-md shadow-zinc-900 rounded-md mt-5">
                <table className="w-full text-sm">
                    <tr>
                        <th className="text-zinc-400 py-2">POS</th>
                        <th className="text-start pl-5 text-zinc-400 py-2">EQUIPO</th>
                        <th className="text-zinc-400 py-2">PJ</th>
                        <th className="text-zinc-400 py-2">PTS</th>
                    </tr>
                    <tr className="border-t border-zinc-700">
                        <td className="text-center text-zinc-300 font-semibold py-2">1</td>
                        <td className="pl-5 text-zinc-300 font-semibold py-2">Manchester City</td>
                        <td className="text-center text-zinc-400 font-semibold py-2">28</td>
                        <td className="text-center text-lime-300 font-semibold py-2">72</td>
                    </tr>
                    <tr className="border-t border-zinc-700">
                        <td className="text-center text-zinc-300 font-semibold py-2">2</td>
                        <td className="pl-5 text-zinc-300 font-semibold py-2">Arsenal</td>
                        <td className="text-center text-zinc-400 font-semibold py-2">28</td>
                        <td className="text-center text-lime-300 font-semibold py-2">68</td>
                    </tr>
                    <tr className="border-t border-zinc-700">
                        <td className="text-center text-zinc-300 font-semibold py-2">3</td>
                        <td className="pl-5 text-zinc-300 font-semibold py-2">Liverpool</td>
                        <td className="text-center text-zinc-400 font-semibold py-2">28</td>
                        <td className="text-center text-lime-300 font-semibold py-2">65</td>
                    </tr>
                    <tr className="border-t border-zinc-700">
                        <td className="text-center text-zinc-300 font-semibold py-2">4</td>
                        <td className="pl-5 text-zinc-300 font-semibold py-2">Aston Villa</td>
                        <td className="text-center text-zinc-400 font-semibold py-2">28</td>
                        <td className="text-center text-lime-300 font-semibold py-2">58</td>
                    </tr>
                </table>
            </div>
        </div>

        <div className="bg-gradient-to-br from-lime-300 to-cyan-500 flex flex-col justify-center items-center gap-3 p-10">
            <MdOutlineSecurity className="w-10 h-10" />
            <h3 className="font-bold text-white text-2xl">¿Listo para comenzar?</h3>
            <p className="text-sm">Únete a miles de organizadores deportivos que ya confían en GoalApp</p>
            <Link to={'/register'} className="text-lime-300 bg-black py-2 px-5 rounded-xl">Crear Cuenta Gratis</Link>
        </div>

        <footer className="bg-zinc-800 grid grid-cols-1 lg:grid-cols-3 justify-start items-start py-10 px-5 sm:px-30 gap-4">
            <div className="flex flex-col justify-center items-start gap-2 p-2">
                <div className="flex flex-row items-center justify-start gap-2 w-1/3">
                    <div className="bg-lime-300 p-1 rounded-md">
                        <TfiCup className="w-3"/>
                    </div>
                    <p className="text-white font-semibold text-sm">GoalApp</p>
                </div>
                <p className="text-zinc-500 text-sm pl-6 lg:pl-0">Plataforma integral de giestión deportiva para ligas, equipos y jugadores.</p>
            </div>
            <div className="flex flex-col justify-center items-start gap-2 p-2">
                <p className="text-white font-semibold text-sm">Contacto</p>
                <div className="flex flex-row justify-center items-center gap-1 pl-6 lg:pl-0">
                    <MdEmail className="text-zinc-500 w-5 h-5" />
                    <p className="text-zinc-500 text-sm">info@sportmanager.com</p>
                </div>
                <div className="flex flex-row justify-center items-center gap-1 pl-6 lg:pl-0">
                    <FaPhoneAlt className="text-zinc-500 w-5 h-5" />
                    <p className="text-zinc-500 text-sm">+1 (234) 567-890</p>
                </div>
                <div className="flex flex-row justify-center items-center gap-1 pl-6 lg:pl-0">
                    <FaLocationDot className="text-zinc-500 w-5 h-5" />
                    <p className="text-zinc-500 text-sm">Av. Deportiva 123, Ciudad Deportiva</p>
                </div>
            </div>
            <div className="flex flex-col justify-center items-start gap-1 p-2">
                <p className="text-white font-semibold text-sm">Enlaces Rápidos</p>
                <a href="#" className="text-zinc-500 text-sm pl-6 lg:pl-0">Acerca de</a>                
                <a href="#" className="text-zinc-500 text-sm pl-6 lg:pl-0">Términos y Condiciones</a>                
                <a href="#" className="text-zinc-500 text-sm pl-6 lg:pl-0">Poítica de Privacidad</a>                
                <a href="#" className="text-zinc-500 text-sm pl-6 lg:pl-0">Ayuda</a>                
            </div>
        </footer>
        </>
    )
}