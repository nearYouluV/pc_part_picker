import { useState, useRef, useEffect } from 'react';
import type { ReactNode } from 'react';
import { createPortal } from 'react-dom';

interface TooltipProps {
    content: ReactNode;
    children: ReactNode;
}

export default function Tooltip({ content, children }: TooltipProps) {
    const [show, setShow] = useState(false);
    const timeoutRef = useRef<number | null>(null);
    const hostRef = useRef<HTMLSpanElement | null>(null);
    const [pos, setPos] = useState<{ left: number; top: number } | null>(null);

    useEffect(() => {
        return () => {
            if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
        };
    }, []);

    const measure = () => {
        const el = hostRef.current;
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { left: r.left + r.width / 2, top: r.top };
    };

    const showDelayed = () => {
        if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
        timeoutRef.current = window.setTimeout(() => {
            setPos(measure());
            setShow(true);
        }, 120);
    };
    const hideDelayed = () => {
        if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
        timeoutRef.current = window.setTimeout(() => setShow(false), 100);
    };

    const onClick = () => {
        if (show) {
            setShow(false);
        } else {
            setPos(measure());
            setShow(true);
        }
    };

    return (
        <span
            ref={hostRef}
            className="relative inline-flex"
            onMouseEnter={showDelayed}
            onMouseLeave={hideDelayed}
            onFocus={showDelayed}
            onBlur={hideDelayed}
            onClick={onClick}
            tabIndex={0}
        >
            {children}
            {show && pos && createPortal(
                <div
                    style={{ left: pos.left, top: pos.top - 8 }}
                    className="fixed z-[99999] -translate-x-1/2 w-max max-w-xs bg-black text-white text-xs rounded-md px-2 py-1 shadow-md"
                >
                    {content}
                </div>,
                document.body
            )}
        </span>
    );
}
