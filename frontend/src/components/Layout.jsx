import Navbar from './Navbar';

export default function Layout({ children }) {
    return (
        <div className="min-h-screen bg-dark-bg text-white font-sans selection:bg-brand-500/30">
            <Navbar />
            <main className="pt-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
                {children}
            </main>
        </div>
    );
}
