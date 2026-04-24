import React, { useState, useRef, useCallback } from 'react';
import WebcamCapture from '../components/WebcamCapture';
import { scanIDDocument } from '../services/api';
import { resizeImage } from '../utils/image';
import {
    ScanLine, Upload, Camera, Loader2, CheckCircle, AlertCircle,
    XCircle, FileText, User, Hash, Calendar, Globe, Users,
    ChevronDown, ChevronUp, Copy, ArrowRight, ShieldCheck
} from 'lucide-react';
import clsx from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

// ── Field display card ──────────────────────────────────────────────────────
const FieldCard = ({ icon: Icon, label, value, confidence }) => {
    const hasValue = value && value !== 'null' && value !== 'None';
    return (
        <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className={clsx(
                "flex items-start gap-3 p-3 rounded-xl border transition-all",
                hasValue
                    ? "bg-white/5 border-white/10 hover:border-brand-500/40"
                    : "bg-white/2 border-white/5 opacity-50"
            )}
        >
            <div className={clsx(
                "p-2 rounded-lg shrink-0 mt-0.5",
                hasValue ? "bg-brand-500/15 text-brand-400" : "bg-white/5 text-gray-500"
            )}>
                <Icon className="h-4 w-4" />
            </div>
            <div className="flex-1 min-w-0">
                <p className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mb-0.5">
                    {label}
                </p>
                <p className={clsx(
                    "font-semibold text-sm truncate",
                    hasValue ? "text-white" : "text-gray-600 italic"
                )}>
                    {hasValue ? value : "Not detected"}
                </p>
            </div>
            {hasValue && confidence !== undefined && (
                <span className={clsx(
                    "text-[10px] font-bold px-2 py-0.5 rounded-full border shrink-0 mt-1",
                    confidence >= 0.8
                        ? "bg-green-500/15 text-green-400 border-green-500/20"
                        : confidence >= 0.5
                            ? "bg-yellow-500/15 text-yellow-400 border-yellow-500/20"
                            : "bg-red-500/15 text-red-400 border-red-500/20"
                )}>
                    {Math.round(confidence * 100)}%
                </span>
            )}
        </motion.div>
    );
};

// ── Confidence ring ─────────────────────────────────────────────────────────
const ConfidenceRing = ({ score }) => {
    const pct = Math.round(score * 100);
    const r = 40;
    const circ = 2 * Math.PI * r;
    const offset = circ - (pct / 100) * circ;
    const color = pct >= 75 ? '#22c55e' : pct >= 45 ? '#eab308' : '#ef4444';

    return (
        <div className="flex flex-col items-center gap-1">
            <svg width="100" height="100" viewBox="0 0 100 100" className="-rotate-90">
                <circle cx="50" cy="50" r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
                <motion.circle
                    cx="50" cy="50" r={r}
                    fill="none"
                    stroke={color}
                    strokeWidth="8"
                    strokeLinecap="round"
                    strokeDasharray={circ}
                    initial={{ strokeDashoffset: circ }}
                    animate={{ strokeDashoffset: offset }}
                    transition={{ duration: 1.2, ease: "easeOut" }}
                />
            </svg>
            <div className="-mt-16 mb-10 text-center">
                <p className="text-2xl font-bold" style={{ color }}>{pct}%</p>
                <p className="text-[10px] text-gray-400 uppercase tracking-wider">Confidence</p>
            </div>
        </div>
    );
};

// ── Main Page ────────────────────────────────────────────────────────────────
export default function IDScanner() {
    const navigate = useNavigate();
    const [mode, setMode] = useState('upload'); // 'camera' | 'upload'
    const [image, setImage] = useState(null);
    const [isDragging, setIsDragging] = useState(false);
    const [isScanning, setIsScanning] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [showRaw, setShowRaw] = useState(false);
    const fileInputRef = useRef(null);

    // ── Helpers ────────────────────────────────────────────────────────────
    const reset = () => {
        setImage(null);
        setResult(null);
        setError(null);
        setShowRaw(false);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    const processImage = useCallback(async (b64) => {
        setIsScanning(true);
        setResult(null);
        setError(null);
        try {
            const resp = await scanIDDocument({ image_base64: b64 });
            setResult(resp.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'OCR scanning failed. Please try again.');
        } finally {
            setIsScanning(false);
        }
    }, []);

    const handleFileChange = async (file) => {
        if (!file) return;
        try {
            const b64 = await resizeImage(file, 1920, 1080);
            setImage(b64);
            await processImage(b64);
        } catch {
            setError('Failed to read image file.');
        }
    };

    // ── Drag-drop ─────────────────────────────────────────────────────────
    const onDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        const file = e.dataTransfer.files?.[0];
        if (file && file.type.startsWith('image/')) handleFileChange(file);
    };

    // ── Use for Enrollment shortcut ───────────────────────────────────────
    const useForEnrollment = () => {
        if (!result || !image) return;
        sessionStorage.setItem('ocr_prefill', JSON.stringify({
            national_id: result.id_number || '',
            full_name: result.full_name || '',
            image_base64: image,
            metadata: result
        }));
        navigate('/enroll');
    };

    // ── Copy rawOCR ───────────────────────────────────────────────────────
    const copyRaw = () => {
        if (result?.raw_ocr_text) {
            navigator.clipboard.writeText(result.raw_ocr_text);
        }
    };

    // ── Field definitions ─────────────────────────────────────────────────
    const fields = result ? [
        { icon: User, label: "Full Name", value: result.full_name, confidence: result.confidence_score },
        { icon: Hash, label: "ID Number", value: result.id_number, confidence: result.confidence_score },
        { icon: Calendar, label: "Date of Birth", value: result.date_of_birth, confidence: result.confidence_score },
        { icon: Globe, label: "Nationality", value: result.nationality, confidence: result.confidence_score },
        { icon: Users, label: "Sex", value: result.sex, confidence: result.confidence_score },
        { icon: FileText, label: "Document Type", value: result.document_type, confidence: result.confidence_score },
    ] : [];

    // ═══════════════════════════════════════════════════════════════════════
    return (
        <div className="max-w-6xl mx-auto py-8 px-4">

            {/* ── Hero ─────────────────────────────────────────────────── */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-10 text-center"
            >
                <div className="inline-flex items-center justify-center p-3 bg-brand-500/10 rounded-2xl mb-4 ring-1 ring-brand-500/20">
                    <ScanLine className="h-8 w-8 text-brand-400" />
                </div>
                <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                    Fayda ID Scanner
                </h1>
                <p className="text-gray-400 mt-2 text-lg max-w-2xl mx-auto">
                    Scan an Ethiopian Fayda National ID card to extract and verify identity fields automatically.
                </p>

                {/* Mode Switcher */}
                <div className="flex justify-center mt-6">
                    <div className="bg-white/5 p-1 rounded-full flex gap-1 border border-white/10">
                        <button
                            type="button"
                            onClick={() => { setMode('upload'); reset(); }}
                            className={clsx(
                                "flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all",
                                mode === 'upload' ? "bg-brand-600 text-white shadow-lg" : "text-gray-400 hover:text-white hover:bg-white/5"
                            )}
                        >
                            <Upload className="h-4 w-4" /> Upload ID
                        </button>
                        <button
                            type="button"
                            onClick={() => { setMode('camera'); reset(); }}
                            className={clsx(
                                "flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all",
                                mode === 'camera' ? "bg-brand-600 text-white shadow-lg" : "text-gray-400 hover:text-white hover:bg-white/5"
                            )}
                        >
                            <Camera className="h-4 w-4" /> Live Capture
                        </button>
                    </div>
                </div>
            </motion.div>

            {/* ── Two-column grid ──────────────────────────────────────── */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

                {/* ── Left: Image input ──────────────────────────────── */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                    className="lg:col-span-7"
                >
                    <div className={clsx(
                        "relative rounded-[2rem] border overflow-hidden min-h-[420px] flex flex-col",
                        "bg-dark-card/50 backdrop-blur-md border-white/5 shadow-2xl"
                    )}>

                        {mode === 'camera' ? (
                            <WebcamCapture
                                onCapture={(b64) => { setImage(b64); processImage(b64); }}
                                onRetake={reset}
                            />
                        ) : (
                            <>
                                {image ? (
                                    /* Preview */
                                    <div className="relative flex-1">
                                        <img
                                            src={image}
                                            alt="Scanned ID"
                                            className="w-full h-full object-contain rounded-2xl"
                                            style={{ maxHeight: '420px' }}
                                        />
                                        <button
                                            onClick={reset}
                                            className="absolute top-4 right-4 bg-black/60 backdrop-blur-md px-3 py-1.5 rounded-lg text-white text-sm hover:bg-black/80 transition flex items-center gap-1.5"
                                        >
                                            <XCircle className="h-4 w-4" /> Clear
                                        </button>
                                    </div>
                                ) : (
                                    /* Drop zone */
                                    <div
                                        className={clsx(
                                            "flex-1 flex flex-col items-center justify-center p-10 m-4 rounded-2xl",
                                            "border-2 border-dashed transition-all duration-200 cursor-pointer",
                                            isDragging
                                                ? "border-brand-500 bg-brand-500/10"
                                                : "border-white/10 hover:border-brand-500/50 bg-black/20"
                                        )}
                                        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                                        onDragLeave={() => setIsDragging(false)}
                                        onDrop={onDrop}
                                        onClick={() => fileInputRef.current?.click()}
                                    >
                                        <ScanLine className={clsx(
                                            "h-16 w-16 mb-4 transition-colors",
                                            isDragging ? "text-brand-400" : "text-gray-600"
                                        )} />
                                        <p className="text-gray-300 font-semibold mb-1 text-center">
                                            Drag & drop your ID card here
                                        </p>
                                        <p className="text-gray-500 text-sm mb-6 text-center">
                                            or click to browse · JPG, PNG, WEBP supported
                                        </p>
                                        <span className="bg-brand-600 hover:bg-brand-500 text-white px-5 py-2.5 rounded-xl font-semibold text-sm transition-all shadow-lg flex items-center gap-2">
                                            <Upload className="h-4 w-4" /> Choose File
                                        </span>
                                        <input
                                            ref={fileInputRef}
                                            type="file"
                                            accept="image/*"
                                            className="hidden"
                                            onChange={(e) => handleFileChange(e.target.files?.[0])}
                                        />
                                    </div>
                                )}
                            </>
                        )}

                        {/* Scanning overlay */}
                        <AnimatePresence>
                            {isScanning && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    className="absolute inset-0 bg-black/70 backdrop-blur-sm flex flex-col items-center justify-center z-20 rounded-[2rem]"
                                >
                                    {/* Animated scan lines */}
                                    <div className="relative w-48 h-48 flex items-center justify-center">
                                        <div className="absolute inset-0 border-2 border-brand-500/40 rounded-2xl" />
                                        <motion.div
                                            className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-brand-400 to-transparent"
                                            animate={{ top: ['0%', '100%', '0%'] }}
                                            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                                        />
                                        <ScanLine className="h-10 w-10 text-brand-400" />
                                    </div>
                                    <p className="text-brand-100 font-semibold mt-6 animate-pulse">
                                        Analysing Document…
                                    </p>
                                    <p className="text-gray-400 text-sm mt-1">
                                        OCR + AI field extraction in progress
                                    </p>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    {/* Tips */}
                    <div className="mt-4 p-4 bg-white/3 rounded-2xl border border-white/5 text-sm text-gray-500 flex gap-3 items-start">
                        <ShieldCheck className="h-5 w-5 text-brand-400/60 shrink-0 mt-0.5" />
                        <span>
                            <strong className="text-gray-300">Tips for best results:</strong> Ensure the full card is visible,
                            well-lit, and held flat. Avoid glare or shadows on the card surface.
                        </span>
                    </div>
                </motion.div>

                {/* ── Right: Results ─────────────────────────────────── */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                    className="lg:col-span-5 flex flex-col gap-4"
                >
                    <div className="bg-dark-card/60 backdrop-blur-md rounded-3xl border border-white/5 shadow-2xl flex flex-col overflow-hidden">
                        {/* Header */}
                        <div className="px-6 py-5 border-b border-white/5 flex items-center justify-between">
                            <h2 className="font-semibold text-lg flex items-center gap-2">
                                <FileText className="h-5 w-5 text-brand-400" /> Extracted Fields
                            </h2>
                            {result && (
                                <span className={clsx(
                                    "text-xs px-2.5 py-1 rounded-full border font-bold",
                                    result.extraction_method === 'llm'
                                        ? "bg-purple-500/15 text-purple-300 border-purple-500/20"
                                        : "bg-blue-500/15 text-blue-300 border-blue-500/20"
                                )}>
                                    {result.extraction_method === 'llm' ? '🤖 AI' : '🔍 Regex'}
                                </span>
                            )}
                        </div>

                        <div className="p-6 flex-1 space-y-5">

                            {/* Empty state */}
                            {!result && !isScanning && !error && (
                                <div className="flex flex-col items-center justify-center py-16 text-gray-600 gap-4">
                                    <div className="p-5 bg-white/3 rounded-full">
                                        <ScanLine className="h-10 w-10 opacity-30" />
                                    </div>
                                    <p className="text-center text-sm max-w-xs">
                                        Upload or capture an ID card to extract identity fields.
                                    </p>
                                </div>
                            )}

                            {/* Loading skeleton */}
                            {isScanning && (
                                <div className="space-y-3">
                                    {[...Array(6)].map((_, i) => (
                                        <div key={i} className="h-14 bg-white/5 rounded-xl animate-pulse" />
                                    ))}
                                </div>
                            )}

                            {/* Error */}
                            {error && !isScanning && (
                                <motion.div
                                    initial={{ opacity: 0, y: 8 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-3 text-red-200"
                                >
                                    <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
                                    <div>
                                        <p className="font-semibold text-red-100">Scan Failed</p>
                                        <p className="text-sm mt-0.5">{error}</p>
                                    </div>
                                </motion.div>
                            )}

                            {/* Results */}
                            {result && !isScanning && (
                                <>
                                    {/* Confidence ring */}
                                    <div className="flex flex-col items-center py-2">
                                        <ConfidenceRing score={result.confidence_score} />
                                        <div className={clsx(
                                            "flex items-center gap-1.5 text-sm font-medium px-3 py-1 rounded-full border",
                                            result.confidence_score >= 0.7
                                                ? "bg-green-500/15 text-green-300 border-green-500/20"
                                                : result.confidence_score >= 0.4
                                                    ? "bg-yellow-500/15 text-yellow-300 border-yellow-500/20"
                                                    : "bg-red-500/15 text-red-300 border-red-500/20"
                                        )}>
                                            {result.confidence_score >= 0.7
                                                ? <><CheckCircle className="h-4 w-4" /> High Confidence</>
                                                : result.confidence_score >= 0.4
                                                    ? <><AlertCircle className="h-4 w-4" /> Partial Match</>
                                                    : <><XCircle className="h-4 w-4" /> Low Confidence</>
                                            }
                                        </div>
                                    </div>

                                    {/* Field cards */}
                                    <div className="space-y-2">
                                        {fields.map((f, i) => (
                                            <FieldCard key={i} {...f} />
                                        ))}
                                    </div>

                                    {/* Use for enrollment CTA */}
                                    <motion.button
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        transition={{ delay: 0.4 }}
                                        onClick={useForEnrollment}
                                        className="w-full flex items-center justify-center gap-2 py-3.5 px-5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-bold transition-all shadow-lg hover:shadow-brand-500/30 hover:-translate-y-0.5"
                                    >
                                        Use for Enrollment <ArrowRight className="h-4 w-4" />
                                    </motion.button>

                                    {/* Raw OCR collapsible */}
                                    <div className="rounded-xl border border-white/5 overflow-hidden">
                                        <button
                                            onClick={() => setShowRaw(!showRaw)}
                                            className="w-full flex items-center justify-between px-4 py-3 text-sm text-gray-400 hover:text-white hover:bg-white/5 transition"
                                        >
                                            <span className="font-medium">Raw OCR Text</span>
                                            {showRaw ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                                        </button>
                                        <AnimatePresence>
                                            {showRaw && (
                                                <motion.div
                                                    initial={{ height: 0 }}
                                                    animate={{ height: 'auto' }}
                                                    exit={{ height: 0 }}
                                                    className="overflow-hidden"
                                                >
                                                    <div className="relative bg-black/40 p-4 border-t border-white/5">
                                                        <button
                                                            onClick={copyRaw}
                                                            className="absolute top-3 right-3 p-1.5 rounded-lg bg-white/5 hover:bg-white/15 text-gray-400 hover:text-white transition"
                                                        >
                                                            <Copy className="h-3.5 w-3.5" />
                                                        </button>
                                                        <pre className="text-xs text-gray-400 whitespace-pre-wrap font-mono leading-relaxed max-h-40 overflow-y-auto pr-6 custom-scrollbar">
                                                            {result.raw_ocr_text || '(empty)'}
                                                        </pre>
                                                    </div>
                                                </motion.div>
                                            )}
                                        </AnimatePresence>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
