/**
 * LoadingSpinner.jsx — Reusable loading spinner component.
 */

import React from "react";

/**
 * @param {Object} props
 * @param {string} [props.size] - Spinner size: "sm", "md", "lg"
 * @param {string} [props.message] - Optional loading message
 * @param {boolean} [props.overlay] - Whether to render as full-screen overlay
 */
export function LoadingSpinner({ size = "md", message, overlay = false }) {
  const sizeMap = { sm: 24, md: 40, lg: 64 };
  const px = sizeMap[size] || sizeMap.md;

  const spinner = (
    <div className={`loading-spinner loading-spinner--${size}`} role="status">
      <svg
        width={px}
        height={px}
        viewBox="0 0 24 24"
        fill="none"
        className="spinner-icon"
        aria-hidden="true"
      >
        <circle
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          strokeDasharray="31.4 31.4"
          className="spinner-circle"
        />
      </svg>
      {message && <p className="spinner-message">{message}</p>}
      <span className="sr-only">Loading</span>
    </div>
  );

  if (overlay) {
    return <div className="loading-overlay">{spinner}</div>;
  }

  return spinner;
}

export default LoadingSpinner;
