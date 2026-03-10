import { Link } from "react-router";
import { IoMdArrowBack } from "react-icons/io";
import foco from '../../../assets/foco-auth.jpeg'
import { useState } from "react";

export default function SendEmailForgottenPasswd() {
    const [email, setEmail] = useState<string>('')
    
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

            <div className="bg-zinc-950 flex justify-center items-center h-full w-full md:w-1/2">
                <div className="bg-zinc-800 p-3 sm:p-10 rounded-lg flex flex-col justify-center gap-9 sm:w-3/5">
                    <Link to={'/login'} className="flex flex-row items-center gap-2">
                        <IoMdArrowBack className="text-zinc-400"/>
                        <p className="text-[12px] text-zinc-400">Volver</p>
                    </Link>
                    <div>
                        <Link to={'/'} className="text-lime-300 font-semibold mb-3">GoalApp</Link>
                        <h2 className="text-white text-2xl font-semibold">¿Olvidaste tu contraseña?</h2>
                        <p className="text-sm text-zinc-400">Ingresa tu correo electrónico y te enviaremos instrucciones para restablecer tu contraseña.</p>
                    </div>

                    <div>
                        <p className="text-sm text-zinc-400 font-semibold">Correo Electrónico</p>
                        <input
                            type="email"
                            placeholder="tu@email.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="focus:outline-none focus:border-transparent w-full bg-zinc-700 p-2 text-sm rounded-sm placeholder:text-zinc-400 text-zinc-400"
                        />
                    
                        <button className="w-full py-2 text-sm bg-lime-300 rounded-full font-semibold mt-10">Acceder</button>
                    </div>
                </div>
            </div>
        </div>
        </>
    )
}