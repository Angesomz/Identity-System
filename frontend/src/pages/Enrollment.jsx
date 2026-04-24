import React, { useState, useEffect, useRef } from 'react';
import WebcamCapture from '../components/WebcamCapture';
import { enrollIdentity } from '../services/api';
import { resizeImage } from '../utils/image';
import { UserPlus, Loader2, CheckCircle, AlertCircle, ScanFace, ShieldCheck, Database, Server, Camera, Upload, XCircle } from 'lucide-react';
import clsx from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';

const ProcessingStep = ({ icon: Icon, label, status }) => (
    <div className={clsx(
        "flex items-center gap-3 p-3 rounded-xl border transition-all duration-500",
        status === 'pending' && "border-white/5 text-gray-500 bg-white/5",
        status === 'active' && "border-brand-500/50 text-brand-400 bg-brand-500/10 shadow-[0_0_15px_rgba(14,165,233,0.1)]",
        status === 'completed' && "border-green-500/50 text-green-400 bg-green-500/10"
    )}>
        <div className={clsx(
            "p-2 rounded-lg transition-colors duration-300",
            status === 'active' ? "bg-brand-500/20" : "bg-white/5",
            status === 'completed' && "bg-green-500/20"
        )}>
            {status === 'active' ? (
                <Loader2 className="h-5 w-5 animate-spin" />
            ) : status === 'completed' ? (
                <CheckCircle className="h-5 w-5" />
            ) : (
                <Icon className="h-5 w-5" />
            )}
        </div>
        <span className="font-medium">{label}</span>
    </div>
);

export default function Enrollment() {
    const [formData, setFormData] = useState({
        national_id: '',
        full_name: '',
        image_base64: null,
    });
    const [isProcessing, setIsProcessing] = useState(false);
    const [processStep, setProcessStep] = useState(0); // 0: Idle, 1: Uploading, 2: Analyzing, 3: Indexing, 4: Done
    const [result, setResult] = useState(null); // { status: 'success' | 'error', message: '' }
    const [mode, setMode] = useState('camera'); // 'camera' or 'upload'
    const fileInputRef = useRef(null);

    // Pre-fill from OCR scanner shortcut
    useEffect(() => {
        const raw = sessionStorage.getItem('ocr_prefill');
        if (raw) {
            try {
                const prefill = JSON.parse(raw);
                setFormData({
                    national_id: prefill.national_id || '',
                    full_name: prefill.full_name || '',
                    image_base64: prefill.image_base64 || null,
                    metadata: prefill.metadata || {}
                });
                if (prefill.image_base64) setMode('upload');
            } catch { /* ignore */ }
            sessionStorage.removeItem('ocr_prefill');
        }
    }, []);

    const handleCapture = (imageSrc) => {
        setFormData({ ...formData, image_base64: imageSrc });
        setResult(null);
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (file) {
            try {
                // Resize image before setting state
                const resizedImage = await resizeImage(file, 1280, 720);
                setFormData({ ...formData, image_base64: resizedImage });
                setResult(null);
            } catch (err) {
                console.error("Error resizing image:", err);
                setResult({ status: 'error', message: "Failed to process image. Please try another file." });
            }
        }
    };

    const handleRetake = () => {
        setFormData({ ...formData, image_base64: null });
        setResult(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    const simulateProgress = async () => {
        setProcessStep(1); // Uploading
        await new Promise(r => setTimeout(r, 600));
        setProcessStep(2); // Analyzing
        await new Promise(r => setTimeout(r, 800));
        setProcessStep(3); // Indexing
        await new Promise(r => setTimeout(r, 600));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!formData.image_base64) {
            setResult({ status: 'error', message: 'Identity capture required.' });
            return;
        }

        setIsProcessing(true);
        setResult(null);

        // Start simulated visual progress in parallel with actual request
        const progressPromise = simulateProgress();

        try {
            const apiPromise = enrollIdentity(formData);
            const [_, response] = await Promise.all([progressPromise, apiPromise]);

            setProcessStep(4);
            setResult({
                status: 'success',
                message: `Identity Enrolled: ${response.data.enrollment_id}`
            });
            // Optional: clear form after success
            // setFormData({ national_id: '', full_name: '', image_base64: null });
        } catch (error) {
            setProcessStep(0);
            setResult({
                status: 'error',
                message: error.response?.data?.detail || 'Enrollment failed.'
            });
        } finally {
            setIsProcessing(false);
        }
    };

    const steps = [
        { icon: Server, label: "Secure Upload" },
        { icon: ScanFace, label: "Biometric Analysis" },
        { icon: Database, label: "Vector Indexing" },
    ];

    return (
        <div className="max-w-6xl mx-auto py-8 px-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-10 text-center"
            >
                <div className="inline-flex items-center justify-center p-3 bg-brand-500/10 rounded-2xl mb-4 ring-1 ring-brand-500/20">
                    <UserPlus className="h-8 w-8 text-brand-400" />
                </div>
                <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                    New Identity Enrollment
                </h1>
                <p className="text-gray-400 mt-2 text-lg max-w-2xl mx-auto">
                    Register individuals into the secure biometric database.
                </p>

                {/* Mode Switcher */}
                <div className="flex justify-center mt-6">
                    <div className="bg-white/5 p-1 rounded-full flex gap-1 border border-white/10">
                        <button
                            type="button"
                            onClick={() => { setMode('camera'); handleRetake(); }}
                            className={clsx(
                                "flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all",
                                mode === 'camera' ? "bg-brand-600 text-white shadow-lg" : "text-gray-400 hover:text-white hover:bg-white/5"
                            )}
                        >
                            <Camera className="h-4 w-4" /> Live Camera
                        </button>
                        <button
                            type="button"
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
                {/* Left Column: Form */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                    className="lg:col-span-5 space-y-6"
                >
                    <div className="bg-dark-card/50 backdrop-blur-xl p-8 rounded-3xl border border-white/5 shadow-2xl relative overflow-hidden">
                        {/* Decorative gradient blob */}
                        <div className="absolute -top-20 -right-20 w-64 h-64 bg-brand-500/10 blur-[100px] rounded-full pointer-events-none"></div>

                        <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                            <ShieldCheck className="text-brand-400" /> Identity Details
                        </h2>

                        <form onSubmit={handleSubmit} className="space-y-5">
                            <div className="space-y-1">
                                <label className="text-sm font-medium text-gray-300 ml-1">
                                    National ID
                                </label>
                                <input
                                    type="text"
                                    required
                                    value={formData.national_id}
                                    onChange={(e) => setFormData({ ...formData, national_id: e.target.value })}
                                    className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500/50 outline-none transition-all placeholder-gray-600 font-mono"
                                    placeholder="ET-1234-5678"
                                />
                            </div>

                            <div className="space-y-1">
                                <label className="text-sm font-medium text-gray-300 ml-1">
                                    Full Name
                                </label>
                                <input
                                    type="text"
                                    required
                                    value={formData.full_name}
                                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                                    className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500/50 outline-none transition-all placeholder-gray-600"
                                    placeholder="Abebe Kebede"
                                />
                            </div>

                            {/* Processing Steps Overlay / Inline */}
                            <AnimatePresence>
                                {(isProcessing || processStep > 0) && (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: 'auto' }}
                                        exit={{ opacity: 0, height: 0 }}
                                        className="space-y-2 overflow-hidden py-2"
                                    >
                                        {steps.map((step, idx) => (
                                            <ProcessingStep
                                                key={idx}
                                                {...step}
                                                status={processStep > idx + 1 ? 'completed' : processStep === idx + 1 ? 'active' : 'pending'}
                                            />
                                        ))}
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            {/* Result Message */}
                            <AnimatePresence>
                                {result && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0 }}
                                        className={clsx(
                                            "p-4 rounded-xl flex items-center gap-3 border backdrop-blur-md",
                                            result.status === 'success' ? "bg-green-500/10 border-green-500/20 text-green-200" : "bg-red-500/10 border-red-500/20 text-red-200"
                                        )}
                                    >
                                        {result.status === 'success' ? <CheckCircle className="h-5 w-5 shrink-0" /> : <AlertCircle className="h-5 w-5 shrink-0" />}
                                        <p className="font-medium">{result.message}</p>
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            <button
                                type="submit"
                                disabled={isProcessing}
                                className={clsx(
                                    "w-full flex items-center justify-center gap-2 py-4 px-6 rounded-xl font-bold text-lg transition-all shadow-lg",
                                    isProcessing
                                        ? "bg-gray-700/50 text-gray-400 cursor-not-allowed"
                                        : "bg-brand-600 hover:bg-brand-500 text-white shadow-brand-500/25 hover:shadow-brand-500/40 hover:-translate-y-0.5"
                                )}
                            >
                                {isProcessing ? (
                                    <>Processing...</>
                                ) : (
                                    <>Enroll Identity <UserPlus className="h-5 w-5" /></>
                                )}
                            </button>
                        </form>
                    </div>
                </motion.div>

                {/* Right Column: Camera / Upload */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                    className="lg:col-span-7"
                >
                    <div className="sticky top-8">
                        <div className="bg-dark-card/50 backdrop-blur-md p-2 rounded-[2rem] border border-white/5 shadow-2xl relative min-h-[400px] flex flex-col">
                            {mode === 'camera' ? (
                                <>
                                    <WebcamCapture onCapture={handleCapture} onRetake={handleRetake} />
                                    <div className="mt-4 flex items-center justify-center gap-2 text-sm text-gray-500">
                                        <ScanFace className="h-4 w-4" />
                                        <span>Position face within the frame. Ensure good lighting.</span>
                                    </div>
                                </>
                            ) : (
                                <div className="flex-1 flex flex-col items-center justify-center p-8 bg-black/20 rounded-xl border-2 border-dashed border-white/10 hover:border-brand-500/50 transition-colors">
                                    {formData.image_base64 ? (
                                        <div className="relative w-full h-full">
                                            <img src={formData.image_base64} alt="Uploaded" className="w-full h-full object-contain rounded-lg" />
                                            <button
                                                type="button"
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
                                                Select a photo for enrollment. High quality images recommended.
                                            </p>
                                            <input
                                                type="file"
                                                ref={fileInputRef}
                                                accept="image/*"
                                                onChange={handleFileUpload}
                                                className="hidden"
                                                id="enrollment-file-upload"
                                            />
                                            <label
                                                htmlFor="enrollment-file-upload"
                                                className="cursor-pointer bg-brand-600 hover:bg-brand-500 text-white px-6 py-3 rounded-xl font-semibold transition-all shadow-lg hover:shadow-brand-500/25 flex items-center gap-2"
                                            >
                                                <Upload className="h-5 w-5" /> Choose Photo
                                            </label>
                                        </>
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
