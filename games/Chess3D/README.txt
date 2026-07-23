WIZARD'S CHESS 3D  (real 3D, Three.js)
======================================
True 3D chess: sculpted marble pieces (real pawn shape, horse-head knight,
crown queen, cross king), a marble board, and pieces that GLIDE across the
board while KNIGHTS HOP in an arc. Captured pieces sink into the board.

TO PLAY  (must be served — three.min.js won't load from a raw file:// path):
  - Double-click  "Play (Windows).bat"   (or run:  python serve.py)
  - Then open  http://localhost:8802

CONTROLS
  - Drag  = orbit the camera around the board
  - Scroll = zoom
  - Click a piece, then click a highlighted square to move.

Full rules (castling, en passant, promotion to queen, check/checkmate).
Strength selector + New Game at the bottom. Runs 100% offline (three.min.js
is bundled in this folder). You play White vs a real chess AI.
