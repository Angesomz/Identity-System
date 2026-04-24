import { Link, useLocation } from 'react-router-dom';
import { ShieldCheck, UserPlus, Search, Menu, X, ScanLine } from 'lucide-react';
import { useState } from 'react';
import clsx from 'clsx';

export default function Navbar() {
    const [isOpen, setIsOpen] = useState(false);
    const location = useLocation();

    const navItems = [
        { name: 'Dashboard', path: '/', icon: ShieldCheck },
        { name: 'Enrollment', path: '/enroll', icon: UserPlus },
        { name: 'Identify', path: '/identify', icon: Search },
        { name: 'ID Scanner', path: '/scan-id', icon: ScanLine },
        { name: 'Identities', path: '/identities', icon: UserPlus },
    ];

    return (
        <nav className="fixed top-0 w-full z-50 bg-dark-bg/80 backdrop-blur-md border-b border-white/10">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    <div className="flex items-center">
                        <Link to="/" className="flex-shrink-0 flex items-center gap-2">
                            <ShieldCheck className="h-8 w-8 text-brand-400" />
                            <span className="text-white font-bold text-xl tracking-wide">INSA Identity</span>
                        </Link>
                    </div>
                    <div className="hidden md:block">
                        <div className="ml-10 flex items-baseline space-x-4">
                            {navItems.map((item) => {
                                const Icon = item.icon;
                                const isActive = location.pathname === item.path;
                                return (
                                    <Link
                                        key={item.name}
                                        to={item.path}
                                        className={clsx(
                                            'flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200',
                                            isActive
                                                ? 'bg-brand-500/10 text-brand-400'
                                                : 'text-gray-300 hover:bg-white/5 hover:text-white'
                                        )}
                                    >
                                        <Icon className="h-4 w-4" />
                                        {item.name}
                                    </Link>
                                );
                            })}
                        </div>
                    </div>
                    <div className="-mr-2 flex md:hidden">
                        <button
                            onClick={() => setIsOpen(!isOpen)}
                            className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-gray-700 focus:outline-none"
                        >
                            {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                        </button>
                    </div>
                </div>
            </div>

            {isOpen && (
                <div className="md:hidden bg-dark-card border-b border-white/10">
                    <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = location.pathname === item.path;
                            return (
                                <Link
                                    key={item.name}
                                    to={item.path}
                                    onClick={() => setIsOpen(false)}
                                    className={clsx(
                                        'flex items-center gap-2 px-3 py-2 rounded-md text-base font-medium',
                                        isActive
                                            ? 'bg-brand-500/10 text-brand-400'
                                            : 'text-gray-300 hover:bg-white/5 hover:text-white'
                                    )}
                                >
                                    <Icon className="h-4 w-4" />
                                    {item.name}
                                </Link>
                            );
                        })}
                    </div>
                </div>
            )}
        </nav>
    );
}
