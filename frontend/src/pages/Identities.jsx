import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Shield, User, Calendar, Loader } from 'lucide-react';

const Identities = () => {
    const [identities, setIdentities] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchIdentities();
    }, []);

    const fetchIdentities = async () => {
        try {
            const response = await fetch('http://localhost:8000/identities');
            const data = await response.json();

            if (data.success) {
                setIdentities(data.identities);
            } else {
                setError('Failed to fetch identities');
            }
        } catch (err) {
            setError('Error connecting to server');
        } finally {
            setLoading(false);
        }
    };

    const filteredIdentities = identities.filter(id =>
        id.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        id.national_id.includes(searchTerm)
    );

    return (
        <div className="max-w-6xl mx-auto p-6">
            <motion.div
                initial={{ y: -20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="mb-8"
            >
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-brand-300 to-indigo-400 mb-2">
                    Enrolled Identities
                </h1>
                <p className="text-gray-400">Manage and view all biometric enrollments.</p>
            </motion.div>

            <div className="mb-6 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 h-5 w-5" />
                <input
                    type="text"
                    placeholder="Search by Name or National ID..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full bg-dark-card border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white focus:ring-2 focus:ring-brand-500 outline-none"
                />
            </div>

            {loading ? (
                <div className="flex justify-center py-20">
                    <Loader className="animate-spin text-brand-500 h-12 w-12" />
                </div>
            ) : error ? (
                <div className="text-red-400 text-center py-10 bg-red-400/10 rounded-xl">
                    {error}
                </div>
            ) : (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="grid gap-4 auto-rows-max"
                >
                    <div className="bg-dark-card border border-white/10 rounded-xl overflow-hidden">
                        <table className="w-full text-left">
                            <thead className="bg-white/5 text-gray-400 uppercase text-sm">
                                <tr>
                                    <th className="p-4">ID</th>
                                    <th className="p-4">Full Name</th>
                                    <th className="p-4">National ID</th>
                                    <th className="p-4">Enrolled Date</th>
                                    <th className="p-4">Status</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {filteredIdentities.map((identity) => (
                                    <tr key={identity.id} className="hover:bg-white/5 transition-colors">
                                        <td className="p-4 font-mono text-gray-500">#{identity.id}</td>
                                        <td className="p-4 font-semibold text-white flex items-center gap-2">
                                            <div className="h-8 w-8 rounded-full bg-brand-500/20 flex items-center justify-center text-brand-400">
                                                <User className="h-4 w-4" />
                                            </div>
                                            {identity.full_name}
                                        </td>
                                        <td className="p-4 text-gray-300 font-mono">{identity.national_id}</td>
                                        <td className="p-4 text-gray-400">
                                            {new Date(identity.created_at).toLocaleDateString()}
                                            <span className="text-xs ml-2 text-gray-600">
                                                {new Date(identity.created_at).toLocaleTimeString()}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            <span className="px-2 py-1 rounded-full text-xs bg-green-500/10 text-green-400 border border-green-500/20">
                                                Active
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        {filteredIdentities.length === 0 && (
                            <div className="p-8 text-center text-gray-500">
                                No identities found matching your search.
                            </div>
                        )}
                    </div>
                </motion.div>
            )}
        </div>
    );
};

export default Identities;
