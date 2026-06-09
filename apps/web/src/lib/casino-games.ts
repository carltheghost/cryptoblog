export interface CasinoGame {
  id: string;
  name: string;
  category: string;
  min_bet: number;
  max_multiplier: number;
  dimension: "3D" | "4D";
  emoji: string;
  gradient: string;
  description: string;
}

export const CASINO_GAMES: CasinoGame[] = [
  { id: "tess-slots", name: "Tess Slots", category: "slots", min_bet: 10, max_multiplier: 50, dimension: "3D", emoji: "🎰", gradient: "from-cyan-500/30 to-violet-600/30", description: "3D hyper-reels with TRD jackpots" },
  { id: "hyper-dice", name: "Hyper Dice", category: "dice", min_bet: 5, max_multiplier: 6, dimension: "3D", emoji: "🎲", gradient: "from-violet-500/30 to-pink-600/30", description: "Roll dual dice in zero-gravity 3D" },
  { id: "quantum-roulette", name: "Quantum Roulette", category: "table", min_bet: 10, max_multiplier: 35, dimension: "3D", emoji: "🎯", gradient: "from-green-500/30 to-cyan-600/30", description: "Spin the quantum wheel — red, black, or number" },
  { id: "crash-orbit", name: "Crash Orbit", category: "crash", min_bet: 5, max_multiplier: 100, dimension: "4D", emoji: "🚀", gradient: "from-orange-500/30 to-red-600/30", description: "4D orbital crash — cash out before implosion" },
  { id: "soul-wheel", name: "Soul Wheel", category: "wheel", min_bet: 5, max_multiplier: 10, dimension: "3D", emoji: "🎡", gradient: "from-gold-500/30 to-amber-600/30", description: "Spin the soul wheel for multipliers" },
  { id: "tess-poker", name: "Tess Poker", category: "cards", min_bet: 20, max_multiplier: 2, dimension: "3D", emoji: "🃏", gradient: "from-indigo-500/30 to-violet-600/30", description: "High-card duel vs the house" },
  { id: "hyper-lottery", name: "Hyper Lottery 4D", category: "lottery", min_bet: 1, max_multiplier: 100, dimension: "4D", emoji: "✨", gradient: "from-fuchsia-500/30 to-cyan-600/30", description: "Pick 4 digits across the tesseract" },
];

export function getGame(id: string) {
  return CASINO_GAMES.find((g) => g.id === id);
}
