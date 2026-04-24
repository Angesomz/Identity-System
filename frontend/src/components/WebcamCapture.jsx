import React, { useRef, useState, useCallback } from 'react';
import Webcam from 'react-webcam';
import { Camera, RefreshCw, CheckCircle, XCircle } from 'lucide-react';
import clsx from 'clsx';

export default function WebcamCapture({ onCapture, onRetake }) {
    const webcamRef = useRef(null);
    const [imgSrc, setImgSrc] = useState(null);

    const capture = useCallback(() => {
        const imageSrc = webcamRef.current.getScreenshot();
        setImgSrc(imageSrc);
        if (onCapture) onCapture(imageSrc);
    }, [webcamRef, onCapture]);

    const retake = () => {
        setImgSrc(null);
        if (onRetake) onRetake();
    };

    const [scanning, setScanning] = useState(true);

    return (
        <div className="relative w-full aspect-video bg-black rounded-3xl overflow-hidden shadow-2xl ring-1 ring-white/10 group">
            {imgSrc ? (
                <img src={imgSrc} alt="captured" className="w-full h-full object-cover" />
            ) : (
                <Webcam
                    audio={false}
                    ref={webcamRef}
                    screenshotFormat="image/jpeg"
                    className="w-full h-full object-cover transform scale-x-[-1]" // Mirror effect
                    videoConstraints={{
                        width: 1280,
                        height: 720,
                        facingMode: "user"
                    }}
                />
            )}

            {/* Tech Overlay */}
            {!imgSrc && (
                <div className="absolute inset-0 pointer-events-none">
                    {/* Scanning Line */}
                    <div className="absolute inset-x-0 h-0.5 bg-brand-400/50 shadow-[0_0_15px_rgba(56,189,248,0.8)] animate-scan-y"></div>

                    {/* Corner Brackets */}
                    <div className="absolute top-8 left-8 w-16 h-16 border-t-4 border-l-4 border-brand-500/50 rounded-tl-xl"></div>
                    <div className="absolute top-8 right-8 w-16 h-16 border-t-4 border-r-4 border-brand-500/50 rounded-tr-xl"></div>
                    <div className="absolute bottom-24 left-8 w-16 h-16 border-b-4 border-l-4 border-brand-500/50 rounded-bl-xl"></div>
                    <div className="absolute bottom-24 right-8 w-16 h-16 border-b-4 border-r-4 border-brand-500/50 rounded-br-xl"></div>

                    {/* Face Frame Guide */}
                    <div className="absolute inset-0 flex items-center justify-center pb-20">
                        <div className="relative w-64 h-80 border-2 border-white/20 rounded-[3rem] border-dashed">
                            <div className="absolute top-1/2 left-0 w-full h-0.5 bg-red-500/20"></div>
                            <div className="absolute left-1/2 top-0 h-full w-0.5 bg-red-500/20"></div>
                        </div>
                    </div>

                    {/* Status Text */}
                    <div className="absolute top-6 left-1/2 -translate-x-1/2 flex items-center gap-2 px-4 py-1 bg-black/50 backdrop-blur-md rounded-full border border-white/10">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-xs font-mono text-green-400">SYSTEM ONLINE // SEARCHING</span>
                    </div>
                </div>
            )}

            {/* Overlay Controls */}
            <div className="absolute inset-x-0 bottom-0 p-6 flex justify-center items-end bg-gradient-to-t from-black/90 via-black/50 to-transparent pt-32">
                {imgSrc ? (
                    <div className="flex gap-4">
                        <button
                            onClick={retake}
                            className="flex items-center gap-2 px-6 py-3 bg-white/10 backdrop-blur-md rounded-xl text-white font-semibold hover:bg-white/20 transition-all border border-white/10"
                        >
                            <RefreshCw className="h-5 w-5" /> Retake
                        </button>
                    </div>
                ) : (
                    <button
                        onClick={capture}
                        className="group flex items-center gap-3 px-8 py-4 bg-brand-600 rounded-xl text-white font-bold text-lg hover:bg-brand-500 transition-all shadow-lg hover:shadow-brand-500/25 ring-1 ring-white/20"
                    >
                        <div className="p-1 bg-white/20 rounded-full">
                            <Camera className="h-6 w-6" />
                        </div>
                        <span className="tracking-wide">CAPTURE IDENTITY</span>
                    </button>
                )}
            </div>
        </div>
    );
}
