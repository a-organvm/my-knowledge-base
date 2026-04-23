/**
 * SystemContext.tsx — React context providing system-wide configuration and state.
 *
 * Centralizes API base URL, feature flags, theme settings, and
 * system health status for all knowledge base UI components.
 */

import React, { createContext, useContext, useState, useEffect } from "react";
import type { ReactNode } from "react";

interface SystemConfig {
  apiBase: string;
  wsUrl: string;
  features: {
    semanticSearch: boolean;
    insightExtraction: boolean;
    smartTagging: boolean;
    relationshipDetection: boolean;
    gamification: boolean;
    rtmOverlay: boolean;
  };
  theme: "light" | "dark" | "system";
}

interface SystemHealth {
  status: "healthy" | "degraded" | "down";
  database: boolean;
  vectorDb: boolean;
  apiServer: boolean;
  lastCheck: string | null;
}

interface SystemContextValue {
  config: SystemConfig;
  health: SystemHealth;
  updateConfig: (partial: Partial<SystemConfig>) => void;
  checkHealth: () => Promise<void>;
}

const defaultConfig: SystemConfig = {
  apiBase: "/api",
  wsUrl: "ws://localhost:3000/ws",
  features: {
    semanticSearch: true,
    insightExtraction: true,
    smartTagging: true,
    relationshipDetection: true,
    gamification: false,
    rtmOverlay: false,
  },
  theme: "system",
};

const defaultHealth: SystemHealth = {
  status: "down",
  database: false,
  vectorDb: false,
  apiServer: false,
  lastCheck: null,
};

const SystemContext = createContext<SystemContextValue>({
  config: defaultConfig,
  health: defaultHealth,
  updateConfig: () => {},
  checkHealth: async () => {},
});

export function useSystem(): SystemContextValue {
  return useContext(SystemContext);
}

interface SystemProviderProps {
  initialConfig?: Partial<SystemConfig>;
  children: ReactNode;
}

export function SystemProvider({ initialConfig, children }: SystemProviderProps) {
  const [config, setConfig] = useState<SystemConfig>({
    ...defaultConfig,
    ...initialConfig,
    features: { ...defaultConfig.features, ...initialConfig?.features },
  });
  const [health, setHealth] = useState<SystemHealth>(defaultHealth);

  const updateConfig = (partial: Partial<SystemConfig>) => {
    setConfig((prev) => ({
      ...prev,
      ...partial,
      features: { ...prev.features, ...partial.features },
    }));
  };

  const checkHealth = async () => {
    try {
      const res = await fetch(`${config.apiBase}/health`);
      if (res.ok) {
        const data = await res.json();
        setHealth({
          status: "healthy",
          database: data.database ?? true,
          vectorDb: data.vectorDb ?? false,
          apiServer: true,
          lastCheck: new Date().toISOString(),
        });
      } else {
        setHealth((prev) => ({
          ...prev,
          status: "degraded",
          apiServer: true,
          lastCheck: new Date().toISOString(),
        }));
      }
    } catch {
      setHealth((prev) => ({
        ...prev,
        status: "down",
        apiServer: false,
        lastCheck: new Date().toISOString(),
      }));
    }
  };

  useEffect(() => {
    checkHealth();
  }, [config.apiBase]);

  return (
    <SystemContext.Provider value={{ config, health, updateConfig, checkHealth }}>
      {children}
    </SystemContext.Provider>
  );
}

export default SystemContext;
