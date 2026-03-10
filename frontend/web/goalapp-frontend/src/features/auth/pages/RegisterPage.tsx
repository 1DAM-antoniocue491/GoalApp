import { Link } from "react-router";
import { FaEye } from "react-icons/fa";
import { FaEyeSlash } from "react-icons/fa6";
import foco from '../../../assets/foco-auth.jpeg'
import { useState } from "react";

export default function RegisterPage() {
    const [name, setName] = useState<string>('')
    const [email, setEmail] = useState<string>('')
    const [firstPasswd, setFirstPasswd] = useState<string>('')
    const [firstPasswdType, setFirstPasswdType] = useState<boolean>(false)
    const [secondPasswd, setSecondPasswd] = useState<string>('')
    const [secondPasswdType, setSecondPasswdType] = useState<boolean>(false)
    const [checkbox, setCheckbox] = useState(false)
    
    return (
        <>
        <div className="bg-zinc-950 min-h-screen flex justify-center md:justify-start items-center ">
            <div className="hidden md:block relative w-1/2">
                <img 
                    src={foco} 
                    alt="Logo del proyecto" 
                    className="w-full h-full object-cover" 
                />
                <div className="absolute inset-0 bg-gradient-to-r from-transparent to-zinc-950 from-30%"></div> 
                <div className="absolute inset-0 bg-gradient-to-b from-transparent to-zinc-950 from-30%"></div> 
                <div className="absolute inset-0 bg-gradient-to-t from-transparent to-zinc-950 from-30%"></div> 
            </div>

            <div className="bg-zinc-950 flex justify-center items-center h-full w-full md:w-1/2 ">
                <div className="bg-zinc-800 p-3 sm:p-10 rounded-lg flex flex-col justify-center gap-9 sm:w-3/5">
                    <div>
                        <Link to={'/login'} className="text-lime-300 font-semibold mb-3">GoalApp</Link>
                        <h2 className="text-white text-2xl font-semibold">Bienvenido</h2>
                    </div>

                    <div className="flex bg-zinc-700 text-sm rounded-sm">
                        <Link to={'/login'} className="w-1/2 text-center m-0.5 mr-0 rounded-sm text-white py-1">Iniciar Sesión</Link>
                        <Link to={'/register'} className="w-1/2 text-center m-0.5 ml-0 rounded-sm text-white py-1 bg-zinc-800">Registrarse</Link>
                    </div>

                    <div>
                        <p className="text-sm text-zinc-400 font-semibold">Nombre</p>
                        <input
                            type="text"
                            placeholder="Juan Pérez"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="focus:outline-none focus:border-transparent w-full bg-zinc-700 p-2 text-sm rounded-sm placeholder:text-sm placeholder:text-zinc-400 text-zinc-400"
                        />

                        <p className="text-sm text-zinc-400 font-semibold mt-3">Correo Electrónico</p>
                        <input
                            type="email"
                            placeholder="tu@email.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="focus:outline-none focus:border-transparent w-full bg-zinc-700 p-2 text-sm rounded-sm placeholder:text-sm placeholder:text-zinc-400 text-zinc-400"
                        />
                    
                        <p className="text-sm text-zinc-400 font-semibold mt-3">Contraseña</p>
                        <div className="relative">
                            <input
                                type={firstPasswdType ? "text" : "password"}
                                placeholder="**********"
                                value={firstPasswd}
                                onChange={(e) => setFirstPasswd(e.target.value)}
                                className="focus:outline-none focus:border-transparent w-full bg-zinc-700 p-2 text-sm rounded-sm placeholder:text-sm placeholder:text-zinc-400 text-zinc-400" 
                            />
                            {
                                firstPasswdType ?
                                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2 rounded-full" onClick={() => setFirstPasswdType(false)}>
                                        <FaEyeSlash className="text-zinc-400"/>
                                    </div>
                                :
                                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2 rounded-full" onClick={() => setFirstPasswdType(true)}>
                                        <FaEye className="text-zinc-400"/>
                                    </div>
                            }
                        </div>

                        <p className="text-sm text-zinc-400 font-semibold mt-3">Repetir contraseña</p>
                        <div className="relative">
                            <input
                                type={secondPasswdType ? "text" : "password"}
                                placeholder="Confirma la contraseña"
                                value={secondPasswd}
                                onChange={(e) => setSecondPasswd(e.target.value)}
                                className="focus:outline-none focus:border-transparent w-full bg-zinc-700 p-2 text-sm rounded-sm placeholder:text-sm placeholder:text-zinc-400 text-zinc-400" 
                            />
                            {
                                secondPasswdType ?
                                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2 rounded-full" onClick={() => setSecondPasswdType(false)}>
                                        <FaEyeSlash className="text-zinc-400"/>
                                    </div>
                                :
                                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2 rounded-full" onClick={() => setSecondPasswdType(true)}>
                                        <FaEye className="text-zinc-400"/>
                                    </div>
                            }
                        </div>

                        <div className="flex flex-row items-center mt-3 gap-2">
                            <input
                                type="checkbox"
                                checked={checkbox}
                                onChange={(e) => setCheckbox(e.target.checked)}
                            />
                            <p className="text-[12px] text-zinc-400">Acepto los términos y condiciones</p>
                        </div>
                    </div>

                    <div>
                        <button className="w-full py-2 text-sm bg-lime-300 rounded-full font-semibold">Acceder</button>
                    </div>
                </div>
            </div>
        </div>
        </>
    )
}