import { FaChevronDown } from "react-icons/fa";
import { IoIosNotificationsOutline, IoMdMenu } from "react-icons/io";
import { useState } from "react";
import { useNavigate } from 'react-router-dom';
import { NavLink } from "react-router-dom";
import { TfiCup } from "react-icons/tfi";

export default function Nav() {
    const navigate = useNavigate();
    const [notifications, setNotification] = useState<boolean>(false);
    const [page, setPage] = useState<string>('');
    const [showMenu, setShowMenu] = useState<boolean>(false)

    const redirection = (pageName: string) => {
        setPage(pageName);
        
        switch (pageName) {
            case "home":
                navigate('/dashboard');
                break;
            case "league":
                navigate('/leagues');
                break;
            case "teams":
                navigate('/teams');
                break;
            case "statistics":
                navigate('/statistics');
                break;
            default:
                navigate('/dashboard');
        }

        console.log(page);
    };

    const navItems = [
    { label: 'Inicio', path: '/dashboard' },
    { label: 'Ligas', path: '/leagues' },
    { label: 'Equipos', path: '/teams' },
    { label: 'Estadísticas', path: '/statistics' },
    ];

    return (
        <>
            <div className="bg-zinc-800 flex flex-col">
                <div className="bg-zinc-800 flex flex-row justify-between items-center h-12 px-2">
                    <div className="flex flex-row items-center justify-center gap-2 md:w-1/3">
                        <div className="bg-lime-300 p-2 rounded-md md:pointer-events-none" onClick={() => setShowMenu(!showMenu)}>
                            <IoMdMenu className="md:hidden w-5 h-5" />
                            <TfiCup className="hidden md:block w-5 h-5" />
                        </div>
                        <p className="text-white font-bold">GoalApp</p>
                    </div>
                    
                    <div className="flex-row items-center gap-2 sm:w-1/3 hidden md:flex">
                        {navItems.map((item) => (
                            <NavLink
                                key={item.path}
                                to={item.path}
                                className={({ isActive }) =>
                                `transition-colors ${isActive ? 'bg-lime-300/15 rounded-lg' : ''}`
                                }
                            >
                                {({ isActive }) => (
                                <div className="rounded-lg px-3">
                                    <p
                                    className={`py-1 font-semibold text-sm ${
                                        isActive
                                        ? 'text-lime-300 border-b-2'
                                        : 'text-zinc-500'
                                    }`}
                                    >
                                    {item.label}
                                    </p>
                                </div>
                                )}
                            </NavLink>
                        ))}
                    </div>

                    <div className="flex flex-row justify-end md:pr-10 items-center gap-2 sm:w-1/3">
                        <div className="relative p-1.5 rounded-full bg-zinc-700 border border-zinc-600">
                            <IoIosNotificationsOutline className="text-zinc-400" />
                            
                            {notifications ? (
                                <div className="absolute top-0 right-0 w-2.5 h-2.5 bg-lime-300 rounded-full border-2 border-zinc-700"></div>
                            ) : null}
                        </div>

                        <div className="flex flex-row items-center justify-between bg-zinc-700 rounded-full p-0.5 gap-1">
                            <div className="bg-gradient-to-br from-lime-300 to-blue-300 rounded-full p-0.5 px-1.5">
                                <p className="font-bold">JD</p>
                            </div>
                            
                            <p className="text-sm text-zinc-400 font-semibold hidden md:block">John D.</p>

                            <FaChevronDown className="w-4 h-4 text-zinc-400 p-1 md:mr-2"/>
                        </div>
                    </div>
                </div>

                <div className={`flex-col items-center gap-2 md:w-1/3 pb-2 px-5 ${ showMenu ? 'flex' : 'hidden'}`}>
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                            `transition-colors w-full ${isActive ? 'bg-lime-300/15 rounded-lg' : ''}`
                            }
                        >
                            {({ isActive }) => (
                            <div className="rounded-lg text-center px-3">
                                <p
                                className={`py-1 font-semibold text-sm ${
                                    isActive
                                    ? 'text-lime-300 border-b-2'
                                    : 'text-zinc-500'
                                }`}
                                >
                                {item.label}
                                </p>
                            </div>
                            )}
                        </NavLink>
                    ))}
                </div>
            </div>
        </>
    )
}