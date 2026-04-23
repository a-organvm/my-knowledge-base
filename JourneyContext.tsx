/**
 * JourneyContext.tsx — React context for tracking user journey through the knowledge base.
 *
 * Maintains navigation history, breadcrumbs, exploration depth,
 * and provides session-level analytics for the gamification layer.
 */

import React, { createContext, useContext, useReducer, useCallback } from "react";
import type { ReactNode } from "react";

interface JourneyStep {
  id: string;
  type: "search" | "view_unit" | "view_tag" | "view_relationship" | "navigate";
  label: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

interface JourneyState {
  steps: JourneyStep[];
  currentDepth: number;
  maxDepth: number;
  sessionStart: string;
  breadcrumbs: JourneyStep[];
}

type JourneyAction =
  | { type: "ADD_STEP"; step: JourneyStep }
  | { type: "GO_BACK"; count?: number }
  | { type: "RESET" };

const initialState: JourneyState = {
  steps: [],
  currentDepth: 0,
  maxDepth: 0,
  sessionStart: new Date().toISOString(),
  breadcrumbs: [],
};

function journeyReducer(state: JourneyState, action: JourneyAction): JourneyState {
  switch (action.type) {
    case "ADD_STEP": {
      const newSteps = [...state.steps, action.step];
      const newDepth = state.currentDepth + 1;
      const newBreadcrumbs = [...state.breadcrumbs, action.step].slice(-10);
      return {
        ...state,
        steps: newSteps,
        currentDepth: newDepth,
        maxDepth: Math.max(state.maxDepth, newDepth),
        breadcrumbs: newBreadcrumbs,
      };
    }
    case "GO_BACK": {
      const count = action.count || 1;
      return {
        ...state,
        currentDepth: Math.max(0, state.currentDepth - count),
        breadcrumbs: state.breadcrumbs.slice(0, -count),
      };
    }
    case "RESET":
      return { ...initialState, sessionStart: new Date().toISOString() };
    default:
      return state;
  }
}

interface JourneyContextValue {
  state: JourneyState;
  addStep: (step: Omit<JourneyStep, "timestamp">) => void;
  goBack: (count?: number) => void;
  reset: () => void;
}

const JourneyContext = createContext<JourneyContextValue>({
  state: initialState,
  addStep: () => {},
  goBack: () => {},
  reset: () => {},
});

export function useJourney(): JourneyContextValue {
  return useContext(JourneyContext);
}

interface JourneyProviderProps {
  children: ReactNode;
}

export function JourneyProvider({ children }: JourneyProviderProps) {
  const [state, dispatch] = useReducer(journeyReducer, initialState);

  const addStep = useCallback((step: Omit<JourneyStep, "timestamp">) => {
    dispatch({
      type: "ADD_STEP",
      step: { ...step, timestamp: new Date().toISOString() },
    });
  }, []);

  const goBack = useCallback((count?: number) => {
    dispatch({ type: "GO_BACK", count });
  }, []);

  const reset = useCallback(() => {
    dispatch({ type: "RESET" });
  }, []);

  return (
    <JourneyContext.Provider value={{ state, addStep, goBack, reset }}>
      {children}
    </JourneyContext.Provider>
  );
}

export default JourneyContext;
