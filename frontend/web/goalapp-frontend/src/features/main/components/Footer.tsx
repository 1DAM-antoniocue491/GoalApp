import { FaPhoneAlt } from "react-icons/fa";
import { FaLocationDot } from "react-icons/fa6";
import { MdEmail } from "react-icons/md";
import { TfiCup } from "react-icons/tfi";

export default function Footer() {
    return (
        <>
        <footer className="bg-zinc-800 grid grid-cols-1 md:grid-cols-3 justify-beetweeen items-start py-10 px-5 lg:px-30 gap-4">
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