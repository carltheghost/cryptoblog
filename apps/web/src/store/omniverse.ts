import { create } from "zustand";

export type Dimension = 1 | 2 | 3 | 4 | 5 | 99;

interface OmniverseState {
  dimension: Dimension;
  overdrive: boolean;
  quantumSuperposed: boolean;
  impossibilityIndex: number;
  paradoxCount: number;
  realityStability: number;
  setDimension: (d: Dimension) => void;
  setOverdrive: (v: boolean) => void;
  setQuantum: (v: boolean) => void;
  hydrate: (data: Partial<Pick<OmniverseState, "dimension" | "overdrive" | "quantumSuperposed" | "impossibilityIndex" | "paradoxCount" | "realityStability">>) => void;
}

export const useOmniverseStore = create<OmniverseState>((set) => ({
  dimension: 3,
  overdrive: false,
  quantumSuperposed: true,
  impossibilityIndex: 0,
  paradoxCount: 0,
  realityStability: 100,
  setDimension: (dimension) =>
    set({ dimension, overdrive: dimension >= 5 || dimension === 99 }),
  setOverdrive: (overdrive) =>
    set((s) => ({ overdrive, dimension: overdrive ? (s.dimension >= 5 ? s.dimension : 5) : s.dimension > 4 ? 4 : s.dimension })),
  setQuantum: (quantumSuperposed) => set({ quantumSuperposed }),
  hydrate: (data) => set((s) => ({ ...s, ...data })),
}));

export const DIMENSION_LABELS: Record<number, string> = {
  1: "1D Linear",
  2: "2D Planar",
  3: "3D Spatial",
  4: "4D Temporal",
  5: "5D Hyper",
  99: "∞ Infinite",
};
