/**
 * UserProfileContext.tsx — React context for user profile state.
 *
 * Manages user preferences, bookmarks, recent searches,
 * and custom tag sets across the knowledge base UI.
 */

import React, { createContext, useContext, useReducer, useEffect, useCallback } from "react";
import type { ReactNode } from "react";

interface UserProfile {
  name: string;
  preferences: {
    searchMode: "fulltext" | "semantic" | "hybrid";
    resultsPerPage: number;
    theme: "light" | "dark" | "system";
    showRelationships: boolean;
    showInsights: boolean;
  };
  bookmarks: string[];
  recentSearches: Array<{ query: string; timestamp: string }>;
  customTags: string[];
}

type ProfileAction =
  | { type: "SET_PREFERENCE"; key: string; value: unknown }
  | { type: "ADD_BOOKMARK"; unitId: string }
  | { type: "REMOVE_BOOKMARK"; unitId: string }
  | { type: "ADD_SEARCH"; query: string }
  | { type: "ADD_CUSTOM_TAG"; tag: string }
  | { type: "REMOVE_CUSTOM_TAG"; tag: string }
  | { type: "LOAD_PROFILE"; profile: UserProfile };

const STORAGE_KEY = "kb-user-profile";

const defaultProfile: UserProfile = {
  name: "default",
  preferences: {
    searchMode: "hybrid",
    resultsPerPage: 20,
    theme: "system",
    showRelationships: true,
    showInsights: true,
  },
  bookmarks: [],
  recentSearches: [],
  customTags: [],
};

function profileReducer(state: UserProfile, action: ProfileAction): UserProfile {
  switch (action.type) {
    case "SET_PREFERENCE":
      return {
        ...state,
        preferences: { ...state.preferences, [action.key]: action.value },
      };
    case "ADD_BOOKMARK":
      if (state.bookmarks.includes(action.unitId)) return state;
      return { ...state, bookmarks: [...state.bookmarks, action.unitId] };
    case "REMOVE_BOOKMARK":
      return {
        ...state,
        bookmarks: state.bookmarks.filter((id) => id !== action.unitId),
      };
    case "ADD_SEARCH":
      return {
        ...state,
        recentSearches: [
          { query: action.query, timestamp: new Date().toISOString() },
          ...state.recentSearches.filter((s) => s.query !== action.query),
        ].slice(0, 50),
      };
    case "ADD_CUSTOM_TAG":
      if (state.customTags.includes(action.tag)) return state;
      return { ...state, customTags: [...state.customTags, action.tag] };
    case "REMOVE_CUSTOM_TAG":
      return {
        ...state,
        customTags: state.customTags.filter((t) => t !== action.tag),
      };
    case "LOAD_PROFILE":
      return { ...defaultProfile, ...action.profile };
    default:
      return state;
  }
}

interface ProfileContextValue {
  profile: UserProfile;
  setPreference: (key: string, value: unknown) => void;
  addBookmark: (unitId: string) => void;
  removeBookmark: (unitId: string) => void;
  addSearch: (query: string) => void;
  addCustomTag: (tag: string) => void;
  removeCustomTag: (tag: string) => void;
}

const ProfileContext = createContext<ProfileContextValue>({
  profile: defaultProfile,
  setPreference: () => {},
  addBookmark: () => {},
  removeBookmark: () => {},
  addSearch: () => {},
  addCustomTag: () => {},
  removeCustomTag: () => {},
});

export function useProfile(): ProfileContextValue {
  return useContext(ProfileContext);
}

export function UserProfileProvider({ children }: { children: ReactNode }) {
  const [profile, dispatch] = useReducer(profileReducer, defaultProfile);

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        dispatch({ type: "LOAD_PROFILE", profile: JSON.parse(stored) });
      }
    } catch {
      // Ignore parse errors
    }
  }, []);

  // Persist to localStorage on change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
    } catch {
      // Ignore storage errors
    }
  }, [profile]);

  const setPreference = useCallback((key: string, value: unknown) => {
    dispatch({ type: "SET_PREFERENCE", key, value });
  }, []);

  const addBookmark = useCallback((unitId: string) => {
    dispatch({ type: "ADD_BOOKMARK", unitId });
  }, []);

  const removeBookmark = useCallback((unitId: string) => {
    dispatch({ type: "REMOVE_BOOKMARK", unitId });
  }, []);

  const addSearch = useCallback((query: string) => {
    dispatch({ type: "ADD_SEARCH", query });
  }, []);

  const addCustomTag = useCallback((tag: string) => {
    dispatch({ type: "ADD_CUSTOM_TAG", tag });
  }, []);

  const removeCustomTag = useCallback((tag: string) => {
    dispatch({ type: "REMOVE_CUSTOM_TAG", tag });
  }, []);

  return (
    <ProfileContext.Provider
      value={{ profile, setPreference, addBookmark, removeBookmark, addSearch, addCustomTag, removeCustomTag }}
    >
      {children}
    </ProfileContext.Provider>
  );
}

export default ProfileContext;
