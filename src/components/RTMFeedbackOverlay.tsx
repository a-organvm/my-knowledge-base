/**
 * RTMFeedbackOverlay.tsx — Real-Time Monitoring feedback overlay.
 *
 * Displays live system metrics, API latency, and search performance
 * as a semi-transparent overlay for development and monitoring.
 */

import React, { useState, useEffect, useRef } from "react";

interface MetricPoint {
  timestamp: number;
  value: number;
}

interface RTMMetrics {
  apiLatencyMs: MetricPoint[];
  searchLatencyMs: MetricPoint[];
  activeConnections: number;
  totalRequests: number;
  errorRate: number;
  uptime: number;
}

interface RTMFeedbackOverlayProps {
  visible?: boolean;
  position?: "top-right" | "top-left" | "bottom-right" | "bottom-left";
  refreshIntervalMs?: number;
  apiBase?: string;
}

export function RTMFeedbackOverlay({
  visible = true,
  position = "bottom-right",
  refreshIntervalMs = 2000,
  apiBase = "/api",
}: RTMFeedbackOverlayProps) {
  const [metrics, setMetrics] = useState<RTMMetrics>({
    apiLatencyMs: [],
    searchLatencyMs: [],
    activeConnections: 0,
    totalRequests: 0,
    errorRate: 0,
    uptime: 0,
  });
  const [minimized, setMinimized] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!visible) return;

    const fetchMetrics = async () => {
      try {
        const res = await fetch(`${apiBase}/health`);
        if (res.ok) {
          const data = await res.json();
          setMetrics((prev) => ({
            ...prev,
            activeConnections: data.connections ?? prev.activeConnections,
            totalRequests: data.totalRequests ?? prev.totalRequests,
            errorRate: data.errorRate ?? prev.errorRate,
            uptime: data.uptime ?? prev.uptime,
            apiLatencyMs: [
              ...prev.apiLatencyMs.slice(-29),
              { timestamp: Date.now(), value: data.latencyMs ?? 0 },
            ],
          }));
        }
      } catch {
        // Silently handle fetch errors in monitoring overlay
      }
    };

    fetchMetrics();
    intervalRef.current = setInterval(fetchMetrics, refreshIntervalMs);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [visible, refreshIntervalMs, apiBase]);

  if (!visible) return null;

  const positionClass = `rtm-overlay rtm-overlay--${position}`;
  const avgLatency =
    metrics.apiLatencyMs.length > 0
      ? Math.round(
          metrics.apiLatencyMs.reduce((s, p) => s + p.value, 0) / metrics.apiLatencyMs.length
        )
      : 0;

  if (minimized) {
    return (
      <div className={positionClass} onClick={() => setMinimized(false)} role="button" tabIndex={0}>
        <span className="rtm-indicator" title="RTM Active">RTM</span>
      </div>
    );
  }

  return (
    <div className={positionClass}>
      <div className="rtm-header">
        <span>RTM Feedback</span>
        <button onClick={() => setMinimized(true)} aria-label="Minimize">_</button>
      </div>
      <div className="rtm-body">
        <div className="rtm-metric">
          <span className="rtm-label">Avg Latency</span>
          <span className="rtm-value">{avgLatency}ms</span>
        </div>
        <div className="rtm-metric">
          <span className="rtm-label">Connections</span>
          <span className="rtm-value">{metrics.activeConnections}</span>
        </div>
        <div className="rtm-metric">
          <span className="rtm-label">Requests</span>
          <span className="rtm-value">{metrics.totalRequests.toLocaleString()}</span>
        </div>
        <div className="rtm-metric">
          <span className="rtm-label">Error Rate</span>
          <span className={`rtm-value ${metrics.errorRate > 0.05 ? "rtm-warn" : ""}`}>
            {(metrics.errorRate * 100).toFixed(1)}%
          </span>
        </div>
        <div className="rtm-metric">
          <span className="rtm-label">Uptime</span>
          <span className="rtm-value">{formatUptime(metrics.uptime)}</span>
        </div>
      </div>
    </div>
  );
}

function formatUptime(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
  return `${Math.floor(seconds / 86400)}d`;
}

export default RTMFeedbackOverlay;
