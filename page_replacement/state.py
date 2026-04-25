import reflex as rx
from pydantic import BaseModel


# ─── Modelos de datos ────────────────────────────────────────────────────────

class CellData(BaseModel):
    value: str = ""
    bg_color: str = "transparent"   # precomputado en Python, sin rx.cond
    text_color: str = "#E8E8F0"
    font_weight: str = "400"
    font_size: str = "13px"


class TableRowData(BaseModel):
    label: str = ""
    cells: list[CellData] = []
    row_type: str = "normal"  # header | ref | frame | bits | pointer | fault | sep


class AlgoResult(BaseModel):
    algo_id: str = ""
    name: str = ""
    color: str = ""
    fault_count: int = 0
    hit_count: int = 0
    total: int = 0
    fault_pct: int = 0       # precomputado para no dividir en la UI
    table_rows: list[TableRowData] = []


# ─── Paleta interna ──────────────────────────────────────────────────────────

_TEXT        = "#E8E8F0"
_TEXT2       = "#8888AA"
_RED         = "#E05252"
_GREEN       = "#3EC97A"
_AMBER       = "#D4A84B"
_BG_FAULT    = "#3D1A1A"
_BG_HEADER   = "#1A1A25"
_TRANSPARENT = "transparent"


# ─── Algoritmos ──────────────────────────────────────────────────────────────

def _pad(frames, n):
    return frames[:] + [None] * (n - len(frames))


def run_fifo(seq, n):
    frames, queue, steps = [], [], []
    for p in seq:
        fault = p not in frames
        replaced = None
        if fault:
            if len(frames) < n:
                frames.append(p); queue.append(p)
            else:
                v = queue.pop(0); replaced = v
                frames[frames.index(v)] = p; queue.append(p)
        steps.append({"frames": _pad(frames, n), "fault": fault,
                       "replaced": replaced, "current": p})
    return steps


def run_optimal(seq, n):
    frames, steps = [], []
    for i, p in enumerate(seq):
        fault = p not in frames
        replaced = None
        if fault:
            if len(frames) < n:
                frames.append(p)
            else:
                ri, mx = 0, -1
                for j, pg in enumerate(frames):
                    try:    nx = seq.index(pg, i + 1)
                    except ValueError: ri = j; break
                    if nx > mx: mx = nx; ri = j
                replaced = frames[ri]; frames[ri] = p
        steps.append({"frames": _pad(frames, n), "fault": fault,
                       "replaced": replaced, "current": p})
    return steps


def run_second_chance(seq, n):
    frames, ptr, steps = [], 0, []
    for p in seq:
        hi = next((i for i, f in enumerate(frames) if f["page"] == p), -1)
        fault = hi == -1
        replaced = None
        if not fault:
            frames[hi]["ref"] = 1
        else:
            if len(frames) < n:
                frames.append({"page": p, "ref": 0})
            else:
                while frames[ptr]["ref"] == 1:
                    frames[ptr]["ref"] = 0
                    ptr = (ptr + 1) % n
                replaced = frames[ptr]["page"]
                frames[ptr] = {"page": p, "ref": 0}
                ptr = (ptr + 1) % n
        pages = [f["page"] for f in frames] + [None] * (n - len(frames))
        bits  = [f["ref"]  for f in frames] + [None] * (n - len(frames))
        steps.append({
            "frames": pages, "ref_bits": bits,
            "pointer": ptr if len(frames) == n else None,
            "fault": fault, "replaced": replaced, "current": p,
        })
    return steps


def run_lru(seq, n):
    frames, last_used, steps = [], {}, []
    for i, p in enumerate(seq):
        fault = p not in frames
        replaced = None
        if fault:
            if len(frames) < n:
                frames.append(p)
            else:
                v = min(frames, key=lambda x: last_used.get(x, -1))
                replaced = v; frames[frames.index(v)] = p
        last_used[p] = i
        steps.append({"frames": _pad(frames, n), "fault": fault,
                       "replaced": replaced, "current": p})
    return steps


def run_mru(seq, n):
    frames, last_used, steps = [], {}, []
    for i, p in enumerate(seq):
        fault = p not in frames
        replaced = None
        if fault:
            if len(frames) < n:
                frames.append(p)
            else:
                v = max(frames, key=lambda x: last_used.get(x, -1))
                replaced = v; frames[frames.index(v)] = p
        last_used[p] = i
        steps.append({"frames": _pad(frames, n), "fault": fault,
                       "replaced": replaced, "current": p})
    return steps


# ─── Helper de celda ─────────────────────────────────────────────────────────

def _cell(value="", bg=_TRANSPARENT, color=_TEXT, bold=False, small=False):
    return CellData(
        value=value, bg_color=bg, text_color=color,
        font_weight="700" if bold else "400",
        font_size="10px" if small else "13px",
    )


# ─── Constructor de filas ─────────────────────────────────────────────────────

def _build_rows(steps, n, is_sc):
    rows = []

    # Paso
    rows.append(TableRowData(
        label="Paso", row_type="header",
        cells=[_cell(str(i+1), bg=_BG_HEADER, color=_TEXT2) for i in range(len(steps))],
    ))
    # Página ref
    rows.append(TableRowData(
        label="Página ref.", row_type="ref",
        cells=[_cell(str(s["current"]),
                     bg=_BG_FAULT if s["fault"] else _TRANSPARENT,
                     color=_RED if s["fault"] else _TEXT,
                     bold=True)
               for s in steps],
    ))
    rows.append(TableRowData(label="", row_type="sep",
                             cells=[_cell() for _ in steps]))

    # Marcos
    for f in range(n):
        cells = []
        for i, s in enumerate(steps):
            pg   = s["frames"][f]
            prev = steps[i-1]["frames"][f] if i > 0 else None
            new  = s["fault"] and pg is not None and pg != prev
            cells.append(_cell(str(pg) if pg is not None else "",
                               color=_AMBER if new else _TEXT, bold=new))
        rows.append(TableRowData(label=f"Marco {f}", row_type="frame", cells=cells))

    if is_sc:
        rows.append(TableRowData(label="", row_type="sep",
                                 cells=[_cell() for _ in steps]))
        for f in range(n):
            cells = []
            for s in steps:
                pg   = s["frames"][f]
                bits = s.get("ref_bits") or []
                bit  = bits[f] if f < len(bits) and bits[f] is not None else -1
                if pg is None:
                    cells.append(_cell(small=True))
                else:
                    cells.append(_cell(str(bit) if bit >= 0 else "",
                                       color=_GREEN if bit == 1 else _TEXT2,
                                       bold=(bit == 1), small=True))
            rows.append(TableRowData(label=f"Bit M{f}", row_type="bits", cells=cells))

        rows.append(TableRowData(
            label="Puntero (SC)", row_type="pointer",
            cells=[_cell(f"→M{s['pointer']}" if s.get("pointer") is not None else "",
                         color=_AMBER, bold=True, small=True)
                   for s in steps],
        ))

    rows.append(TableRowData(label="", row_type="sep",
                             cells=[_cell() for _ in steps]))
    rows.append(TableRowData(
        label="Fallo", row_type="fault",
        cells=[_cell("F" if s["fault"] else "",
                     bg=_BG_FAULT if s["fault"] else _TRANSPARENT,
                     color=_RED, bold=True)
               for s in steps],
    ))
    return rows


# ─── Metadatos ───────────────────────────────────────────────────────────────

ALGO_META = [
    ("fifo",    "FIFO",               "#185FA5", run_fifo,          False),
    ("optimal", "Óptimo",             "#0F6E56", run_optimal,       False),
    ("sc",      "Segunda Oportunidad","#993C1D", run_second_chance, True),
    ("lru",     "LRU",                "#534AB7", run_lru,           False),
    ("mru",     "MRU",                "#993556", run_mru,           False),
]


# ─── Estado ──────────────────────────────────────────────────────────────────

class PageState(rx.State):
    sequence: str = "1234125"
    num_frames: int = 3

    use_fifo: bool = True
    use_optimal: bool = True
    use_sc: bool = True
    use_lru: bool = True
    use_mru: bool = True

    results: list[AlgoResult] = []
    error: str = ""
    ran: bool = False

    @rx.event
    def set_sequence(self, val: str):
        self.sequence = val

    @rx.event
    def set_frames(self, val: str):
        try:
            n = int(val)
            if 1 <= n <= 10:
                self.num_frames = n
        except (ValueError, TypeError):
            pass

    @rx.event
    def toggle_fifo(self, val: bool):    self.use_fifo = val
    @rx.event
    def toggle_optimal(self, val: bool): self.use_optimal = val
    @rx.event
    def toggle_sc(self, val: bool):      self.use_sc = val
    @rx.event
    def toggle_lru(self, val: bool):     self.use_lru = val
    @rx.event
    def toggle_mru(self, val: bool):     self.use_mru = val

    @rx.event
    def run_simulation(self):
        seq_str = self.sequence.strip()
        if not seq_str or not seq_str.isdigit():
            self.error = "La secuencia solo puede contener dígitos (0–9)."
            return
        if not (1 <= self.num_frames <= 10):
            self.error = "Los marcos deben estar entre 1 y 10."
            return
        active = {"fifo": self.use_fifo, "optimal": self.use_optimal,
                  "sc": self.use_sc, "lru": self.use_lru, "mru": self.use_mru}
        selected = [m for m in ALGO_META if active[m[0]]]
        if not selected:
            self.error = "Selecciona al menos un algoritmo."
            return

        self.error = ""
        seq = [int(c) for c in seq_str]
        n   = self.num_frames
        self.results = []

        for algo_id, name, color, runner, is_sc in selected:
            steps  = runner(seq, n)
            faults = sum(1 for s in steps if s["fault"])
            total  = len(steps)
            self.results.append(AlgoResult(
                algo_id=algo_id, name=name, color=color,
                fault_count=faults, hit_count=total - faults,
                total=total,
                fault_pct=int(faults * 100 / total) if total else 0,
                table_rows=_build_rows(steps, n, is_sc),
            ))
        self.ran = True
