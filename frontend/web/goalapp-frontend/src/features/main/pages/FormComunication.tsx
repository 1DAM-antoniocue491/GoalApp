import Header from "../components/Header";
import { TfiCup } from "react-icons/tfi";
import { IoMdPerson } from "react-icons/io";
import { useState } from "react";
import Footer from "../components/Footer";

export default function FormComunication() {
    const [name, setName] = useState<string>("")
    const [email, setEmail] = useState<string>("")
    const [phone, setPhone] = useState<string>("")
    const [message, setMessage] = useState<string>("")
    
    return (
        <>
        <Header />
        <div className="bg-zinc-900 flex flex-col justify-center items-center p-3 sm:p-10 gap-2">
            <div className="bg-lime-300 p-2 rounded-md">
                <TfiCup className="w-8 h-8"/>
            </div>
            <h1 className="text-white text-xl sm:text-3xl font-semibold text-center">Solicita la Creación de tu Liga</h1>
            <p className="text-white text-center sm:w-4/5 mb-5 ">Completa el formulario y nuestro equipo se encargará de configurar tu liga deportiva con todos los detalles necesarios</p>

            <div className="bg-zinc-800 p-5 rounded-lg w-full sm:w-4/5">
                <p className="text-white font-semibold">Nombre Completo <span className="text-red-500">*</span></p>
                <div className="flex flex-row items-center bg-zinc-700 px-4 py-2 rounded-xl gap-3 mt-2 mb-5">
                    <IoMdPerson className="text-zinc-400"/>
                    <input
                        onChange={(e) => setName(e.target.value)}
                        value={name}
                        type="text"
                        placeholder="Juan Pérez"
                        className="focus:outline-none focus:border-transparent text-zinc-400 placeholder-zinc-400 placeholder:text-sm text-sm w-full"
                    />
                </div>

                <p className="text-white font-semibold">Correo Electrónico <span className="text-red-500">*</span></p>
                <div className="flex flex-row items-center bg-zinc-700 px-4 py-2 rounded-xl gap-3 mt-2 mb-5">
                    <IoMdPerson className="text-zinc-400"/>
                    <input
                        onChange={(e) => setEmail(e.target.value)}
                        value={email}
                        type="text"
                        placeholder="tu@email.com"
                        className="focus:outline-none focus:border-transparent text-zinc-400 placeholder-zinc-400 placeholder:text-sm text-sm w-full"
                    />
                </div>

                <p className="text-white font-semibold">Teléfono de Contacto <span className="text-red-500">*</span></p>
                <div className="flex flex-row items-center bg-zinc-700 px-4 py-2 rounded-xl gap-3 mt-2 mb-5">
                    <IoMdPerson className="text-zinc-400"/>
                    <input
                        onChange={(e) => setPhone(e.target.value)}
                        value={phone}
                        type="text"
                        placeholder="+1 (234) 567-890"
                        className="focus:outline-none focus:border-transparent text-zinc-400 placeholder-zinc-400 placeholder:text-sm text-sm w-full"
                    />
                </div>

                <p className="text-white font-semibold">Mensaje / Detalles de la liga <span className="text-red-500">*</span></p>
                <div className="flex flex-row bg-zinc-700 px-4 py-2 rounded-xl gap-3 mt-2 mb-2">
                    <IoMdPerson className="text-zinc-400 mt-1"/>
                    <textarea
                        onChange={(e) => setMessage(e.target.value)}
                        value={message}
                        placeholder="Escribe los detalles de tu liga: nombre, deporte, número de equipos, ubicación, etc."
                        className="focus:outline-none focus:border-transparent text-zinc-400 placeholder-zinc-400 placeholder:text-sm text-sm w-full h-40"
                    />
                </div>

                <p className="text-[12px] text-white">Incluye toda la informacion relevante para que podamos crear tu liga de manera efectiva</p>

                <button className="w-full bg-lime-300 py-3 rounded-2xl font-semibold mt-5">Enviar Solicitud</button>
            </div>

            <div className="flex flex-col md:flex-row gap-3 mt-5 w-full sm:w-4/5">
                <div className="bg-zinc-800 p-4 rounded-lg w-full border border-zinc-500">
                    <p className="text-white font-semibold">¿Qué incluye?</p>
                    <ul className="list-disc text-zinc-500 text-sm marker:text-lime-300 pl-5">
                        <li>Configuración completa de la liga</li>
                        <li>Gestión de equipos y jugadores</li>
                        <li>Sistema de calendario automatizado</li>
                        <li>Tabla de posiciones en tiempo real</li>
                    </ul>
                </div>

                <div className="bg-zinc-800 p-4 rounded-lg w-full border border-zinc-500">
                    <p className="text-white font-semibold">Tiempo de respuesta</p>
                    <p className="text-zinc-500 text-sm">Nuestro equipo revisará tu solicitud y te contactará en un plazo de:</p>
                    <p className="w-full bg-lime-300 text-center p-2 rounded-xl font-bold mt-2">5 días</p>
                </div>
            </div>
        </div>

        <Footer />
        </>
    )
}