import { create } from "zustand";

export type PlatformMode = "centralized" | "decentralized";

interface PlatformState {
  mode: PlatformMode;
  tessId: string;
  setMode: (mode: PlatformMode) => void;
}

export const usePlatformStore = create<PlatformState>((set) => ({
  mode: "centralized",
  tessId: "TRD-8F7C-29D1",
  setMode: (mode) => set({ mode }),
}));
