"use client";

import { useEffect, useRef } from "react";
import { useOmniverseStore } from "@/store/omniverse";

const VERTS = [
  [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
  [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],
  [0, 0, 0],
];
const EDGES = [
  [0, 1], [1, 2], [2, 3], [3, 0],
  [4, 5], [5, 6], [6, 7], [7, 4],
  [0, 4], [1, 5], [2, 6], [3, 7],
  [0, 8], [1, 8], [2, 8], [3, 8], [4, 8], [5, 8], [6, 8], [7, 8],
];

function project(
  x: number, y: number, z: number, w: number,
  dim: number, t: number, cx: number, cy: number, scale: number
) {
  const rot4 = dim >= 4 ? Math.sin(t * 0.4) * 0.6 : 0;
  const rot5 = dim >= 5 ? Math.cos(t * 0.25) * 0.8 : 0;
  const inf = dim === 99 ? Math.sin(t * 2) * 0.3 : 0;
  const wx = x + w * rot4 * 0.3;
  const wy = y + w * rot5 * 0.2;
  const wz = z + inf;
  const rz = Math.cos(t * 0.5) * wx - Math.sin(t * 0.5) * wz;
  const rx = Math.sin(t * 0.5) * wx + Math.cos(t * 0.5) * wz;
  const ry = wy + Math.sin(t * 0.3) * rx * 0.2;
  const dist = 4 + (dim >= 5 ? 1.5 : 0) + (dim === 99 ? Math.sin(t) : 0);
  const f = scale / (dist - rz * 0.3);
  return { x: cx + rx * f, y: cy + ry * f, depth: rz };
}

export function TesseractField() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { dimension, overdrive } = useOmniverseStore();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let frame = 0;
    let raf = 0;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    const draw = () => {
      frame += overdrive ? 0.04 : 0.015;
      const w = canvas.width;
      const h = canvas.height;
      ctx.clearRect(0, 0, w, h);

      if (dimension < 4 && !overdrive) {
        raf = requestAnimationFrame(draw);
        return;
      }

      const cx = w / 2;
      const cy = h / 2;
      const scale = dimension === 99 ? 180 : 120 + dimension * 15;
      const alpha = dimension === 99 ? 0.12 : overdrive ? 0.1 : 0.05;

      const points = VERTS.map(([x, y, z], i) => {
        const w4 = i === 8 ? 0 : Math.sin(frame + i) * (dimension >= 5 ? 0.5 : 0);
        return { ...project(x, y, z, w4, dimension, frame, cx, cy, scale), i };
      });

      ctx.lineWidth = dimension >= 5 ? 1.2 : 0.8;
      for (const [a, b] of EDGES) {
        const pa = points[a];
        const pb = points[b];
        const depth = (pa.depth + pb.depth) / 2;
        const hue = dimension === 99 ? (frame * 40 + depth * 30) % 360 : 190 + depth * 20;
        ctx.strokeStyle = `hsla(${hue}, 80%, 60%, ${alpha * (1 + depth * 0.1)})`;
        ctx.beginPath();
        ctx.moveTo(pa.x, pa.y);
        ctx.lineTo(pb.x, pb.y);
        ctx.stroke();
      }

      for (const p of points) {
        if (p.i === 8) {
          ctx.fillStyle = `rgba(255, 215, 0, ${alpha * 3})`;
          ctx.beginPath();
          ctx.arc(p.x, p.y, overdrive ? 4 : 2, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      if (dimension === 99) {
        for (let i = 0; i < 24; i++) {
          const ang = frame * 0.5 + (i / 24) * Math.PI * 2;
          const r = 80 + Math.sin(frame + i) * 40;
          ctx.fillStyle = `rgba(138, 43, 226, ${0.03 + Math.sin(frame + i) * 0.02})`;
          ctx.beginPath();
          ctx.arc(cx + Math.cos(ang) * r, cy + Math.sin(ang) * r, 2, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      raf = requestAnimationFrame(draw);
    };

    draw();
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
    };
  }, [dimension, overdrive]);

  if (dimension < 4 && !overdrive) return null;

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none fixed inset-0 z-[1] opacity-80"
      aria-hidden
    />
  );
}
