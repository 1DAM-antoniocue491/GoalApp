import React from "react";
import Nav from "../../../components/Nav";
import { TfiCup } from "react-icons/tfi";
import { MdOutlineSecurity } from "react-icons/md";
import { IoPersonAddSharp } from "react-icons/io5";
import { FaRegClock } from "react-icons/fa";

export default function DashboardPage() {

    const quickActions = [
        { icon: TfiCup, label: "+ Nueva Liga" },
        { icon: MdOutlineSecurity, label: "+ Nuevo Equipo" },
        { icon: IoPersonAddSharp, label: "+ Añadir Jugador" },
    ];

    const liveMatches = Array(3).fill({
        league: "La Liga",
        home: "Atlético de Madrid",
        away: "Sevilla",
        score: "1 - 0",
        minute: "67'"
    });

    const recentResults = Array(3).fill({
        league: "La Liga",
        home: "Atlético de Madrid",
        away: "Sevilla",
        score: "1 - 0",
        status: "FT"
    });

    const upcomingMatches = [
        { teams: "Sevilla VS Betis", league: "La Liga", time: "Hoy, 21:00" },
        { teams: "Sevilla VS Betis", league: "La Liga", time: "Hoy, 21:00" }
    ];

    const activities = Array(3).fill({
        title: "Nuevo jugador añadido",
        team: "FC Barcelona",
        time: "Hace 2 horas"
    });

    const summary = [
        { label: "Ligas Activas", value: 8, color: "text-lime-300" },
        { label: "Equipos", value: 64, color: "text-blue-400" },
        { label: "Jugadores", value: 1248, color: "text-blue-400" },
        { label: "Partidos Hoy", value: 12, color: "text-lime-300" }
    ];

    return (
        <>
        <Nav />

        <div className="flex flex-col bg-zinc-950 p-5 sm:px-10 gap-5 sm:gap-10">

            <h1 className="text-white text-2xl font-semibold">
                Hola, Juan Pérez
            </h1>

            {/* USER CARD */}
            <div className="flex flex-row justify-between items-center bg-linear-to-r from-zinc-800 to-zinc-700 rounded-lg p-3">

                <div className="flex flex-col gap-1 justify-center w-full sm:w-auto">
                    <p className="text-zinc-500 text-sm">Bienvenido de vuelta 👋​</p>
                    <h3 className="text-white text-lg font-semibold">John Doe</h3>

                    <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                        <p className="bg-lime-300/25 text-lime-300 text-sm px-2 rounded-full">
                            Administrador
                        </p>
                        <p className="bg-blue-300/25 text-blue-300 text-sm px-2 rounded-full">
                            Gestionar roles
                        </p>
                    </div>
                </div>

                <div className="bg-linear-to-br from-lime-300 to-blue-500 border-lime-300 p-2 rounded-md hidden sm:block">
                    <TfiCup className="w-7 h-7"/>
                </div>

            </div>


            {/* QUICK ACTIONS */}
            <div className="flex flex-col gap-2">

                <p className="text-white font-semibold text-md">
                    Acciones Rápidas
                </p>

                <div className="flex flex-col md:flex-row items-center justify-between gap-2">

                    {quickActions.map((action, i) => {
                        const Icon = action.icon;

                        return (
                            <div
                                key={i}
                                className="flex flex-col justify-center items-center bg-zinc-800 p-5 rounded-xl gap-2 w-full md:w-1/3"
                            >

                                <div className="bg-lime-300/25 border-lime-300 p-2 rounded-md">
                                    <Icon className="text-lime-300"/>
                                </div>

                                <p className="text-white font-semibold text-md">
                                    {action.label}
                                </p>

                            </div>
                        );
                    })}

                </div>
            </div>


            {/* LIVE MATCHES */}
            <div className="flex flex-col gap-2">

                <div className="flex flex-row items-end justify-between">

                    <div className="flex flex-row items-center gap-2">
                        <div className="bg-red-500 w-2 h-2 rounded-full"></div>
                        <p className="text-white font-semibold text-md">
                            Partidos en vivo
                        </p>
                        <p className="text-red-500 text-[12px] bg-red-500/25 rounded-full px-2 text-center">
                            {liveMatches.length}
                        </p>
                    </div>

                    <a href="" className="text-blue-400 text-sm hover:underline hidden">
                        Ver todos
                    </a>

                </div>

                <div className="flex flex-col gap-2">

                    {liveMatches.map((match, i) => (
                        <div
                            key={i}
                            className="flex flex-col gap-4 bg-zinc-900 p-3 rounded-xl border border-red-500/25"
                        >

                            <div className="flex flex-row justify-between items-center">

                                <p className="text-zinc-500 text-[12px]">
                                    {match.league}
                                </p>

                                <div className="flex flex-row items-center gap-1.5">
                                    <div className="bg-red-500 w-2 h-2 rounded-full"></div>
                                    <p className="text-red-500 text-[12px]">EN VIVO</p>
                                    <p className="text-red-500 text-[10px] bg-red-500/25 rounded-full px-2 text-center">
                                        {match.minute}
                                    </p>
                                </div>

                            </div>

                            <div className="flex flex-col md:flex-row gap-2 justify-between items-center">
                                <p className="text-zinc-300 text-[12px] font-semibold">
                                    {match.home}
                                </p>

                                <p className="text-zinc-300 bg-zinc-800 px-3 rounded-lg font-semibold">
                                    {match.score}
                                </p>

                                <p className="text-zinc-300 text-[12px] font-semibold">
                                    {match.away}
                                </p>
                            </div>

                        </div>
                    ))}

                </div>
            </div>


            {/* RECENT RESULTS */}
            <div className="flex flex-col gap-2">

                <div className="flex flex-row items-end justify-between">
                    <p className="text-white font-semibold text-md">
                        Resultados recientes
                    </p>
                    <a href="" className="text-blue-400 text-sm hover:underline">
                        Ver todos
                    </a>
                </div>

                <div className="flex flex-col gap-2">

                    {recentResults.map((match, i) => (
                        <div key={i}>

                            {/* DESKTOP */}
                            <div className="hidden sm:flex flex-row justify-between items-end gap-4 bg-zinc-900 p-3 rounded-xl">

                                <div className="flex flex-col gap-2">
                                    <p className="text-zinc-500 text-[12px]">
                                        {match.league}
                                    </p>
                                    <p className="text-zinc-300 text-[12px] font-semibold">
                                        {match.home}
                                    </p>
                                </div>

                                <div className="flex flex-col items-center">
                                    <p className="text-zinc-300 bg-zinc-800 px-3 rounded-lg font-semibold">
                                        {match.score}
                                    </p>
                                    <p className="text-zinc-600 text-[10px]">
                                        {match.status}
                                    </p>
                                </div>

                                <p className="text-zinc-300 text-[12px] font-semibold">
                                    {match.away}
                                </p>

                            </div>


                            {/* MOBILE */}
                            <div className="flex flex-row justify-between items-center gap-4 bg-zinc-900 p-3 rounded-xl px-7 sm:hidden">

                                <div>
                                    <p className="text-zinc-500 text-[12px]">
                                        {match.league}
                                    </p>
                                    <p className="text-zinc-600 text-[10px]">
                                        {match.status}
                                    </p>
                                </div>

                                <div className="flex flex-col justify-center items-center gap-1">

                                    <p className="text-zinc-300 text-[12px] font-semibold">
                                        {match.home}
                                    </p>

                                    <p className="text-zinc-300 bg-zinc-800 px-3 rounded-lg font-semibold">
                                        {match.score}
                                    </p>

                                    <p className="text-zinc-300 text-[12px] font-semibold">
                                        {match.away}
                                    </p>

                                </div>

                            </div>

                        </div>
                    ))}

                </div>

            </div>


            {/* UPCOMING MATCHES */}
            <div className="flex flex-col gap-2">

                <div className="flex flex-row items-end justify-between">
                    <p className="text-white font-semibold text-md">
                        Próximos partidos
                    </p>
                </div>

                <div className="flex flex-col gap-2">

                    {upcomingMatches.map((match, i) => (
                        <div
                            key={i}
                            className="flex flex-col sm:flex-row justify-between sm:items-center gap-2 bg-zinc-900 px-3 py-2 rounded-xl"
                        >

                            <div className="flex flex-row gap-2 items-center">

                                <FaRegClock className="text-zinc-500"/>

                                <div>
                                    <p className="text-zinc-300 text-[12px] font-semibold">
                                        {match.teams}
                                    </p>

                                    <p className="text-zinc-500 text-[12px]">
                                        {match.league}
                                    </p>
                                </div>

                            </div>

                            <p className="text-blue-400 text-sm bg-blue-400/25 px-3 rounded-full">
                                {match.time}
                            </p>

                        </div>
                    ))}

                </div>

            </div>


            {/* ACTIVITY + SUMMARY */}
            <div className="flex flex-col md:flex-row gap-3">


                {/* ACTIVITY */}
                <div className="flex flex-col gap-5 bg-zinc-900 rounded-xl p-5 w-full md:w-1/2">

                    <p className="text-white font-semibold text-md">
                        Actividad Reciente
                    </p>

                    {activities.map((activity, i) => (
                        <div key={i} className="flex flex-row gap-3">

                            <div className="bg-green-500 w-2 h-2 rounded-full mt-1.5"></div>

                            <div>

                                <p className="text-white text-sm h-4">
                                    {activity.title}
                                </p>

                                <p className="text-lime-300 h-5">
                                    {activity.team}
                                </p>

                                <p className="text-zinc-500 text-[12px]">
                                    {activity.time}
                                </p>

                            </div>

                        </div>
                    ))}

                </div>


                {/* SUMMARY */}
                <div className="flex flex-col gap-5 bg-zinc-900 rounded-xl p-5 w-full md:w-1/2">

                    <p className="text-white font-semibold text-md">
                        Resumen
                    </p>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">

                        {summary.map((item, i) => (
                            <div key={i} className="bg-zinc-800 rounded-lg p-3">

                                <p className="text-zinc-500 text-sm">
                                    {item.label}
                                </p>

                                <p className={`${item.color} font-bold text-3xl`}>
                                    {item.value}
                                </p>

                            </div>
                        ))}

                    </div>

                </div>


            </div>


        </div>
        </>
    );
}