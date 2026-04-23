/**
 * ObserverProtocol.tsx — Observer pattern component for real-time knowledge base updates.
 *
 * Subscribes to WebSocket events and dispatches state updates
 * to child components via React context.
 */

import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";

interface ObserverEvent {
  type: "unit_created" | "unit_updated" | "unit_deleted" | "search" | "tag_added" | "relationship_created";
  payload: Record<string, unknown>;
  timestamp: string;
}

interface ObserverContextValue {
  connected: boolean;
  lastEvent: ObserverEvent | null;
  events: ObserverEvent[];
  subscribe: (type: string, handler: (event: ObserverEvent) => void) => () => void;
}

const ObserverContext = createContext<ObserverContextValue>({
  connected: false,
  lastEvent: null,
  events: [],
  subscribe: () => () => {},
});

export function useObserver(): ObserverContextValue {
  return useContext(ObserverContext);
}

interface ObserverProtocolProps {
  wsUrl?: string;
  maxEvents?: number;
  children: ReactNode;
}

export function ObserverProtocol({
  wsUrl = "ws://localhost:3000/ws",
  maxEvents = 100,
  children,
}: ObserverProtocolProps) {
  const [connected, setConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<ObserverEvent | null>(null);
  const [events, setEvents] = useState<ObserverEvent[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const subscribersRef = useRef<Map<string, Set<(event: ObserverEvent) => void>>>(new Map());

  useEffect(() => {
    const connect = () => {
      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => setConnected(true);
        ws.onclose = () => {
          setConnected(false);
          // Reconnect after 3 seconds
          setTimeout(connect, 3000);
        };
        ws.onerror = () => ws.close();
        ws.onmessage = (msg) => {
          try {
            const event: ObserverEvent = JSON.parse(msg.data);
            setLastEvent(event);
            setEvents((prev) => [event, ...prev].slice(0, maxEvents));

            // Notify subscribers
            const handlers = subscribersRef.current.get(event.type);
            if (handlers) {
              handlers.forEach((handler) => handler(event));
            }
          } catch {
            // Ignore malformed messages
          }
        };
      } catch {
        setTimeout(connect, 3000);
      }
    };

    connect();

    return () => {
      wsRef.current?.close();
    };
  }, [wsUrl, maxEvents]);

  const subscribe = (type: string, handler: (event: ObserverEvent) => void) => {
    if (!subscribersRef.current.has(type)) {
      subscribersRef.current.set(type, new Set());
    }
    subscribersRef.current.get(type)!.add(handler);

    return () => {
      subscribersRef.current.get(type)?.delete(handler);
    };
  };

  return (
    <ObserverContext.Provider value={{ connected, lastEvent, events, subscribe }}>
      {children}
    </ObserverContext.Provider>
  );
}

export default ObserverProtocol;
