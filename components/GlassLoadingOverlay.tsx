
import React, { useState, useEffect, useRef } from 'react';

interface GlassLoadingOverlayProps {
    progress: number;
    totalFiles?: number;
    completedCount?: number;
}

export const GlassLoadingOverlay: React.FC<GlassLoadingOverlayProps> = ({
    progress,
    totalFiles = 1,
    completedCount = 0
}) => {
    const [isPaused, setIsPaused] = useState(false);
    const [localProgress, setLocalProgress] = useState(progress);
    const [stats, setStats] = useState({
        completed: 0,
        total: totalFiles,
        remaining: totalFiles,
        remainingTime: 0
    });

    const particlesRef = useRef<HTMLDivElement>(null);

    // Sync local progress with prop, but allow for smooth animation
    useEffect(() => {
        if (!isPaused) {
            setLocalProgress(progress);
        }
    }, [progress, isPaused]);

    // Update stats based on props
    useEffect(() => {
        setStats({
            completed: completedCount,
            total: totalFiles,
            remaining: totalFiles - completedCount,
            // Mock remaining time calculation
            remainingTime: Math.max(0, Math.ceil((100 - localProgress) / 10))
        });
    }, [localProgress, totalFiles, completedCount]);

    // Particle System
    useEffect(() => {
        const container = particlesRef.current;
        if (!container) return;

        const createParticle = () => {
            if (isPaused) return;
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.bottom = '0';
            particle.style.animationDelay = `${Math.random() * 2}s`;
            particle.style.animationDuration = `${4 + Math.random() * 4}s`;
            container.appendChild(particle);

            setTimeout(() => {
                particle.remove();
            }, 8000);
        };

        const interval = setInterval(createParticle, 1000);
        return () => clearInterval(interval);
    }, [isPaused]);

    // Format time helper
    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fadeIn">
            {/* Background Particles Container */}
            <div ref={particlesRef} className="absolute inset-0 overflow-hidden pointer-events-none z-0" />

            {/* Main Glass Container */}
            <div className="glass rounded-3xl p-6 md:p-8 w-full max-w-lg mx-4 relative z-10 animate-fadeInScale">

                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-400 to-indigo-500 flex items-center justify-center shadow-lg shadow-indigo-500/30">
                            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <div>
                            <h2 className="text-white font-semibold text-lg glow-text">Processing Files</h2>
                            <p className="text-gray-400 text-sm">Estimated time remaining</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className={`status-dot ${isPaused ? 'status-paused' : localProgress >= 100 ? 'status-complete' : 'status-active'}`}></span>
                        <span className="text-gray-300 text-sm font-medium">
                            {isPaused ? 'Paused' : localProgress >= 100 ? 'Complete' : 'Active'}
                        </span>
                    </div>
                </div>

                {/* Progress Container */}
                <div className="mb-6">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-gray-300 text-sm font-medium">Progress</span>
                        <span className="text-white text-lg font-bold glow-text">{Math.round(localProgress)}%</span>
                    </div>
                    <div className="progress-container">
                        <div
                            className="progress-fill"
                            style={{ width: `${localProgress}%` }}
                        />
                    </div>
                    {/* Subtle shadow below progress bar */}
                    <div className="h-1 w-full rounded-full bg-indigo-500/20 mt-1 blur-sm"></div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="glass bg-black/20 rounded-xl p-3 text-center border-none">
                        <p className="text-gray-400 text-xs mb-1">Completed</p>
                        <p className="text-white font-semibold text-lg">{stats.completed}/{stats.total}</p>
                    </div>
                    <div className="glass bg-black/20 rounded-xl p-3 text-center border-none">
                        <p className="text-gray-400 text-xs mb-1">Remaining</p>
                        <p className="text-white font-semibold text-lg">{stats.remaining}</p>
                    </div>
                    <div className="glass bg-black/20 rounded-xl p-3 text-center border-none">
                        <p className="text-gray-400 text-xs mb-1">Time Left</p>
                        <p className="text-white font-semibold text-lg">
                            {localProgress >= 100 ? 'Done!' : formatTime(stats.remainingTime * 2)}
                        </p>
                    </div>
                </div>

                {/* Buttons (Visual only since actual control is handled by parent/backend) */}
                <div className={`flex gap-3 transition-opacity duration-300 ${localProgress >= 100 ? 'opacity-0 pointer-events-none hidden' : 'opacity-100'}`}>
                    <button
                        onClick={() => setIsPaused(!isPaused)}
                        className="btn-glass flex-1 py-3 px-4 rounded-xl text-white font-medium flex items-center justify-center gap-2 hover:text-white"
                    >
                        {isPaused ? (
                            <>
                                <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Resume
                            </>
                        ) : (
                            <>
                                <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Pause
                            </>
                        )}
                    </button>
                </div>

                {/* Completion Message */}
                {localProgress >= 100 && (
                    <div className="text-center py-2 animate-fadeIn">
                        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-green-400 to-emerald-500 mb-4 animate-pulse shadow-lg shadow-emerald-500/30">
                            <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                        <h3 className="text-white text-xl font-semibold mb-2">Processing Complete!</h3>
                        <p className="text-gray-400 mb-4">All files have been processed successfully.</p>
                    </div>
                )}

            </div>
        </div>
    );
};
