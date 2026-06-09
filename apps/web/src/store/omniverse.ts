import { create } from "zustand";

export type Dimension = 1 | 2 | 3 | 4 | 5 | 99;

interface OmniverseState {
  dimension: Dimension;
  overdrive: boolean;
  quantumSuperposed: boolean;
  setDimension: (d: Dimension) => void;
  setOverdrive: (v: boolean) => void;
  setQuantum: (v: boolean) => void;
}

export const useOmniverseStore = create<OmniverseState>((set) => ({
  dimension: 3,
  overdrive: false,
  quantumSuperposed: true,
  setDimension: (dimension) => set({ dimension, overdrive: dimension >= 5 || dimension === 99 }),
  setOverdrive: (overdrive) => set({ overdrive, dimension: overdrive ? 5 : 3 }),
  setQuantum: (quantumSuperposed) => set({ quantumSuperposed }),
}));

export const DIMENSION_LABELS: Record<number, string> = {
  1: "1D Linear",
  2: "2D Planar",
  3: "3D Spatial",
  4: "4D Temporal",
  5: "5D Hyper",
  99: "∞ Infinite",
};
