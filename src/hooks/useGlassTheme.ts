import { useState, useEffect } from 'react';

export const useGlassTheme = () => {
    // Basic detection of dark mode class on html element
    const [isDark, setIsDark] = useState(false);

    useEffect(() => {
        const checkDarkMode = () => {
            setIsDark(document.documentElement.classList.contains('dark'));
        };

        // Initial check
        checkDarkMode();

        // Observer for class changes on html
        const observer = new MutationObserver(checkDarkMode);
        observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });

        return () => observer.disconnect();
    }, []);

    const theme = isDark ? {
        // Dark Theme
        backgroundGradient: 'linear-gradient(to bottom right, #0f172a, #1e1b4b)',
        border: 'rgba(255, 255, 255, 0.1)',
        primary: 'rgba(30, 41, 59, 0.6)', // slate-800 with opacity
        secondary: 'rgba(15, 23, 42, 0.4)', // slate-900 with opacity
        text: '#f8fafc',
        textSecondary: '#94a3b8',
        accent: '#8b5cf6' // violet-500
    } : {
        // Light Theme
        backgroundGradient: 'linear-gradient(to bottom right, #f8fafc, #eff6ff)',
        border: 'rgba(255, 255, 255, 0.3)',
        primary: 'rgba(255, 255, 255, 0.65)',
        secondary: 'rgba(255, 255, 255, 0.4)',
        text: '#1e293b',
        textSecondary: '#475569',
        accent: '#6366f1' // indigo-500
    };

    return { theme };
};
