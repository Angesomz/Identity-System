import React, { useState, useRef } from 'react';
import WebcamCapture from '../components/WebcamCapture';
import { identifyFace } from '../services/api';
import { Search, Loader2, User, AlertTriangle, CheckCircle, XCircle, Upload, Camera } from 'lucide-react';
import clsx from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';
import { resizeImage } from '../utils/image';

export default function Identification() {
    const [image, setImage] = useState(null);
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const [mode, setMode] = useState('camera'); // 'camera' or 'upload'
    const fileInputRef = useRef(null);

    const handleCapture = async (imageSrc) => {
        setImage(imageSrc);
        processIdentification(imageSrc);
    };

    // ... existing imports

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (file) {
            try {
                // Resize image before setting state and sending to API
                const resizedImage = await resizeImage(file, 1280, 720); // Resize to HD or similar
                setImage(resizedImage);
                processIdentification(resizedImage);
            } catch (err) {
                console.error("Error resizing image:", err);
                setError("Failed to process image. Please try another file.");
            }
        }
    };

    const processIdentification = async (imageSrc) => {
        setLoading(true);
        setResults(null);
        setError(null);

        try {
            const response = await identifyFace({ image_base64: imageSrc });
            setResults(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Identification failed.');
        } finally {
            setLoading(false);
        }
    };

    const handleRetake = () => {
        setImage(null);
        setResults(null);
        setError(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    return (
        <div className="max-w-6xl mx-auto py-8 px-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8 text-center"
            >
                <h1 className="text-3xl font-bold flex items-center justify-center gap-3">
                    <Search className="text-brand-400" />
                    Live Identification
                </h1>
                <p className="text-gray-400 mt-2">
                    Real-time biometric search against the million-scale database.
                </p>

                {/* Mode Switcher */}
                <div className="flex justify-center mt-6">
                    <div className="bg-white/5 p-1 rounded-full flex gap-1 border border-white/10">
                        <button
                            onClick={() => { setMode('camera'); handleRetake(); }}
                            className={clsx(
                                "flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all",
                                mode === 'camera' ? "bg-brand-600 text-white shadow-lg" : "text-gray-400 hover:text-white hover:bg-white/5"
                            )}
                        >
                            <Camera className="h-4 w-4" /> Live Camera
                        </button>
                        <button
                            onClick={() => { setMode('upload'); handleRetake(); }}
                            className={clsx(
                                "flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all",
                                mode === 'upload' ? "bg-brand-600 text-white shadow-lg" : "text-gray-400 hover:text-white hover:bg-white/5"
                            )}
                        >
                            <Upload className="h-4 w-4" /> Upload Photo
                        </button>
                    </div>
                </div>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Left Column: Input Source */}
                <motion.div
                    className="lg:col-span-7 space-y-4"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                >
                    <div className="bg-dark-card p-1 rounded-2xl border border-white/5 shadow-xl overflow-hidden relative min-h-[400px] flex flex-col">
                        {mode === 'camera' ? (
                            <WebcamCapture onCapture={handleCapture} onRetake={handleRetake} />
                        ) : (
                            <div className="flex-1 flex flex-col items-center justify-center p-8 bg-black/20 rounded-xl border-2 border-dashed border-white/10 hover:border-brand-500/50 transition-colors">
                                {image ? (
                                    <div className="relative w-full h-full">
                                        <img src={image} alt="Uploaded" className="w-full h-full object-contain rounded-lg" />
                                        <button
                                            onClick={handleRetake}
                                            className="absolute bottom-4 right-4 bg-black/50 backdrop-blur-md px-4 py-2 rounded-lg text-white hover:bg-black/70 transition-colors flex items-center gap-2"
                                        >
                                            <XCircle className="h-4 w-4" /> Clear
                                        </button>
                                    </div>
                                ) : (
                                    <>
                                        <Upload className="h-16 w-16 text-gray-600 mb-4" />
                                        <p className="text-gray-400 mb-6 text-center max-w-sm">
                                            Select an image from your device to identify. Supports JPG, PNG.
                                        </p>
                                        <input
                                            type="file"
                                            ref={fileInputRef}
                                            accept="image/*"
                                            onChange={handleFileUpload}
                                            className="hidden"
                                            id="file-upload"
                                        />
                                        <label
                                            htmlFor="file-upload"
                                            className="cursor-pointer bg-brand-600 hover:bg-brand-500 text-white px-6 py-3 rounded-xl font-semibold transition-all shadow-lg hover:shadow-brand-500/25 flex items-center gap-2"
                                        >
                                            <Upload className="h-5 w-5" /> Choose File
                                        </label>
                                    </>
                                )}
                            </div>
                        )}

                        {/* Loading Overlay */}
                        {loading && (
                            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm flex flex-col items-center justify-center z-20 rounded-2xl">
                                <Loader2 className="h-12 w-12 text-brand-400 animate-spin mb-4" />
                                <p className="text-brand-100 font-medium animate-pulse">Analyzing Biometrics...</p>
                            </div>
                        )}
                    </div>
                </motion.div>

                {/* Right Column: Results */}
                <motion.div
                    className="lg:col-span-5"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <div className="bg-dark-card rounded-2xl border border-white/5 shadow-xl h-full flex flex-col max-h-[600px]">
                        <div className="p-6 border-b border-white/5 bg-white/2">
                            <h2 className="text-xl font-semibold flex items-center gap-2">
                                <Search className="h-5 w-5 text-brand-400" /> Analysis Results
                            </h2>
                        </div>

                        <div className="p-6 flex-1 overflow-y-auto custom-scrollbar">
                            {!image && !loading && (
                                <div className="h-full flex flex-col items-center justify-center text-gray-500 space-y-4 py-12">
                                    <div className="p-4 bg-white/5 rounded-full">
                                        <User className="h-12 w-12 opacity-30" />
                                    </div>
                                    <p className="text-center max-w-xs">
                                        Capture a photo or upload an image to start the identification process.
                                    </p>
                                </div>
                            )}

                            {error && (
                                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-200 flex items-start gap-3">
                                    <AlertTriangle className="h-5 w-5 shrink-0 mt-0.5" />
                                    <div>
                                        <h4 className="font-semibold text-red-100">Analysis Error</h4>
                                        <p className="text-sm mt-1">{error}</p>
                                    </div>
                                </div>
                            )}

                            {results && (
                                <div className="space-y-6">
                                    <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
                                        <span className="text-gray-400">Match Status</span>
                                        <span className={clsx(
                                            "px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1.5",
                                            results.status === "Match Found" ? "bg-green-500/20 text-green-300 border border-green-500/30" :
                                                results.status === "Uncertain" ? "bg-yellow-500/20 text-yellow-300 border border-yellow-500/30" :
                                                    "bg-red-500/20 text-red-300 border border-red-500/30"
                                        )}>
                                            {results.status === "Match Found" ? <CheckCircle className="h-3.5 w-3.5" /> : <AlertTriangle className="h-3.5 w-3.5" />}
                                            {results.status}
                                        </span>
                                    </div>

                                    {results.status === "Match Found" && results.person ? (
                                        <div className="space-y-4">
                                            <p className="text-xs text-gray-500 uppercase tracking-widest font-bold ml-1">Verified Identity</p>
                                            <motion.div
                                                initial={{ opacity: 0, scale: 0.95 }}
                                                animate={{ opacity: 1, scale: 1 }}
                                                className="p-4 bg-gradient-to-br from-green-500/10 to-green-500/5 rounded-xl border border-green-500/30 shadow-lg"
                                            >
                                                <div className="flex justify-between items-start mb-3">
                                                    <div>
                                                        <div className="text-xs text-green-400 mb-1">National ID</div>
                                                        <h3 className="font-bold text-xl text-white tracking-wide">
                                                            {results.person.national_id}
                                                        </h3>
                                                    </div>
                                                    <div className="flex flex-col items-end">
                                                        <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider mb-1 bg-green-500/20 text-green-400">
                                                            Verified
                                                        </span>
                                                        <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                                                            {(results.confidence * 100).toFixed(1)}%
                                                        </span>
                                                    </div>
                                                </div>

                                                {/* Visual Score Bar */}
                                                <div className="h-1.5 w-full bg-black/50 rounded-full overflow-hidden">
                                                    <motion.div
                                                        initial={{ width: 0 }}
                                                        animate={{ width: `${results.confidence * 100}%` }}
                                                        transition={{ delay: 0.5, duration: 1 }}
                                                        className="h-full rounded-full bg-green-500"
                                                    />
                                                </div>

                                                <div className="mt-4 pt-3 border-t border-green-500/20 text-sm text-gray-300 grid grid-cols-2 gap-x-4 gap-y-2">
                                                    <div className="col-span-2 mb-1">
                                                        <span className="text-[10px] uppercase tracking-widest font-bold text-green-400">Core Identity Fields</span>
                                                    </div>

                                                    <div className="flex flex-col">
                                                        <span className="text-[10px] uppercase text-gray-500">Legal Name</span>
                                                        <span className="font-medium text-white">{results.person.full_name}</span>
                                                    </div>

                                                    {results.person.metadata && results.person.metadata.date_of_birth && (
                                                        <div className="flex flex-col">
                                                            <span className="text-[10px] uppercase text-gray-500">Date of Birth</span>
                                                            <span className="font-medium text-white">{results.person.metadata.date_of_birth}</span>
                                                        </div>
                                                    )}

                                                    {results.person.metadata && results.person.metadata.sex && (
                                                        <div className="flex flex-col">
                                                            <span className="text-[10px] uppercase text-gray-500">Sex</span>
                                                            <span className="font-medium text-white">{results.person.metadata.sex}</span>
                                                        </div>
                                                    )}

                                                    {results.person.metadata && results.person.metadata.nationality && (
                                                        <div className="flex flex-col">
                                                            <span className="text-[10px] uppercase text-gray-500">Nationality</span>
                                                            <span className="font-medium text-white">{results.person.metadata.nationality}</span>
                                                        </div>
                                                    )}
                                                </div>
                                            </motion.div>
                                        </div>
                                    ) : results.status === "Uncertain" && results.candidates ? (
                                        <div className="space-y-4">
                                            <p className="text-xs text-gray-500 uppercase tracking-widest font-bold ml-1">Possible Candidates</p>
                                            {results.candidates.map((match, idx) => (
                                                <motion.div
                                                    key={idx}
                                                    initial={{ opacity: 0, scale: 0.95 }}
                                                    animate={{ opacity: 1, scale: 1 }}
                                                    transition={{ delay: idx * 0.1 }}
                                                    className="p-4 bg-gradient-to-br from-white/10 to-white/5 rounded-xl border border-white/10 hover:border-yellow-500/50 transition-all group shadow-lg"
                                                >
                                                    <div className="flex justify-between items-start mb-3">
                                                        <div>
                                                            <div className="text-xs text-gray-400 mb-1">Database ID</div>
                                                            <h3 className="font-bold text-xl text-white group-hover:text-yellow-400 transition-colors tracking-wide">
                                                                #{match.id}
                                                            </h3>
                                                        </div>
                                                        <div className="flex flex-col items-end">
                                                            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider mb-1 bg-yellow-500/20 text-yellow-400">
                                                                Uncertain
                                                            </span>
                                                            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                                                                {(match.score * 100).toFixed(1)}%
                                                            </span>
                                                        </div>
                                                    </div>

                                                    {/* Visual Score Bar */}
                                                    <div className="h-1.5 w-full bg-black/50 rounded-full overflow-hidden">
                                                        <motion.div
                                                            initial={{ width: 0 }}
                                                            animate={{ width: `${match.score * 100}%` }}
                                                            transition={{ delay: 0.5, duration: 1 }}
                                                            className={"h-full rounded-full bg-yellow-500"}
                                                        />
                                                    </div>
                                                </motion.div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="text-center py-10 text-gray-500 bg-white/2 rounded-xl border border-white/5 border-dashed">
                                            <XCircle className="h-12 w-12 mx-auto mb-3 text-red-500/50" />
                                            <p className="text-red-300 mb-1">{results.status || "No reliable match found."}</p>
                                            {results.confidence && <p className="text-xs mt-2">Highest Peak: {(results.confidence * 100).toFixed(1)}%</p>}
                                            <p className="text-sm mt-2">Try adjusting the lighting or angle.</p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
