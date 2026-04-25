import reflex as rx
from .state import PageState, AlgoResult, TableRowData, CellData

BG       = "#0D0D0F"
BG_CARD  = "#13131A"
BG_CARD2 = "#1A1A25"
BORDER   = "#2A2A3A"
TEXT     = "#E8E8F0"
TEXT2    = "#8888AA"
ACCENT   = "#4F6EF7"
RED      = "#E05252"
GREEN    = "#3EC97A"
AMBER    = "#D4A84B"
FONT     = "'Inter', 'Segoe UI', sans-serif"
MONO     = "'JetBrains Mono', 'Fira Mono', monospace"

CARD_STYLE = {
    "background": BG_CARD,
    "border": f"1px solid {BORDER}",
    "border_radius": "10px",
    "padding": "20px 24px",
}

LABEL_STYLE = {
    "font_size": "11px",
    "color": TEXT2,
    "font_weight": "500",
    "letter_spacing": "0.06em",
    "text_transform": "uppercase",
}


# ─── Badge simple (evita props inexistentes en rx.badge) ─────────────────────

def _badge(children: list, bg: str, color: str) -> rx.Component:
    return rx.box(
        *children,
        background=bg,
        color=color,
        border_radius="5px",
        padding="2px 10px",
        font_size="12px",
        font_weight="500",
        white_space="nowrap",
    )


# ─── Input section ───────────────────────────────────────────────────────────

def input_section() -> rx.Component:
    # CORRECTO: hijos primero, luego **kwargs
    return rx.box(
        rx.flex(
            rx.vstack(
                rx.text("Secuencia de páginas", **LABEL_STYLE),
                rx.input(
                    value=PageState.sequence,
                    on_change=PageState.set_sequence,
                    placeholder="ej. 423422234422",
                    font_family=MONO,
                    letter_spacing="3px",
                    font_size="18px",
                    background=BG_CARD2,
                    border=f"1px solid {BORDER}",
                    border_radius="7px",
                    color=TEXT,
                    padding="8px 14px",
                    width="100%",
                ),
                align="start",
                flex="1",
                min_width="200px",
            ),
            rx.vstack(
                rx.text("Marcos", **LABEL_STYLE),
                rx.input(
                    value=PageState.num_frames.to_string(),
                    on_change=PageState.set_frames,
                    type="number",
                    min="1",
                    max="10",
                    background=BG_CARD2,
                    border=f"1px solid {BORDER}",
                    border_radius="7px",
                    color=TEXT,
                    padding="8px 14px",
                    font_size="18px",
                    font_family=MONO,
                    width="100px",
                ),
                align="start",
            ),
            rx.vstack(
                rx.text("\u00a0", **LABEL_STYLE),
                rx.button(
                    "Ejecutar \u2197",
                    on_click=PageState.run_simulation,
                    background=ACCENT,
                    color="white",
                    border_radius="7px",
                    padding="8px 22px",
                    font_size="14px",
                    font_weight="600",
                    cursor="pointer",
                    border="none",
                ),
                align="start",
            ),
            gap="16px",
            align="end",
            flex_wrap="wrap",
        ),
        # ↑ hijos primero — kwargs al final
        margin_bottom="16px",
        **CARD_STYLE,
    )


# ─── Selector de algoritmos ───────────────────────────────────────────────────

def _algo_check(label: str, dot_color: str, checked, on_change) -> rx.Component:
    return rx.hstack(
        rx.checkbox(checked=checked, on_change=on_change),
        rx.box(
            width="10px", height="10px",
            border_radius="50%",
            background=dot_color,
            flex_shrink="0",
        ),
        rx.text(label, font_size="13px", color=TEXT),
        spacing="2",
        align="center",
    )


def algo_selector() -> rx.Component:
    return rx.box(
        rx.text("Algoritmos", margin_bottom="12px", **LABEL_STYLE),
        rx.flex(
            _algo_check("FIFO",                "#185FA5", PageState.use_fifo,    PageState.toggle_fifo),
            _algo_check("Optimo",              "#0F6E56", PageState.use_optimal, PageState.toggle_optimal),
            _algo_check("Segunda Oportunidad", "#993C1D", PageState.use_sc,      PageState.toggle_sc),
            _algo_check("LRU",                 "#534AB7", PageState.use_lru,     PageState.toggle_lru),
            _algo_check("MRU",                 "#993556", PageState.use_mru,     PageState.toggle_mru),
            gap="20px",
            flex_wrap="wrap",
            align="center",
        ),
        rx.cond(
            PageState.error != "",
            rx.text(PageState.error, color=RED, font_size="12px", margin_top="10px"),
            rx.box(),
        ),
        # kwargs al final
        margin_bottom="24px",
        **CARD_STYLE,
    )


# ─── Celda ───────────────────────────────────────────────────────────────────

def render_cell(cell: CellData) -> rx.Component:
    return rx.table.cell(
        rx.text(
            cell.value,
            font_size=cell.font_size,
            font_family=MONO,
            font_weight=cell.font_weight,
            color=cell.text_color,
        ),
        text_align="center",
        min_width="36px",
        height="28px",
        padding="0 4px",
        border=f"0.5px solid {BORDER}",
        background=cell.bg_color,
        vertical_align="middle",
    )


# ─── Fila ────────────────────────────────────────────────────────────────────

def render_row(row: TableRowData) -> rx.Component:
    return rx.cond(
        row.row_type == "sep",
        rx.table.row(
            rx.table.cell(
                height="6px",
                border="none",
                padding="0",
                background="transparent",
            ),
        ),
        rx.table.row(
            rx.table.cell(
                rx.text(
                    row.label,
                    font_size="11px",
                    color=TEXT2,
                    font_family=FONT,
                    white_space="nowrap",
                ),
                text_align="right",
                padding_right="12px",
                min_width="150px",
                border="none",
                background="transparent",
                vertical_align="middle",
            ),
            rx.foreach(row.cells, render_cell),
            background=rx.cond(row.row_type == "header", BG_CARD2, "transparent"),
        ),
    )


# ─── Tabla de algoritmo ───────────────────────────────────────────────────────

def algo_table(result: AlgoResult) -> rx.Component:
    return rx.box(
        rx.flex(
            rx.hstack(
                rx.box(
                    width="10px", height="10px",
                    border_radius="50%",
                    background=result.color,
                    flex_shrink="0",
                ),
                rx.text(result.name, font_size="14px", font_weight="600", color=TEXT),
                spacing="2",
                align="center",
            ),
            rx.flex(
                _badge(
                    [rx.text("Fallos: ", display="inline"),
                     rx.text(result.fault_count.to_string(), display="inline"),
                     rx.text("/", display="inline"),
                     rx.text(result.total.to_string(), display="inline")],
                    bg="#3D1A1A", color=RED,
                ),
                _badge(
                    [rx.text("Aciertos: ", display="inline"),
                     rx.text(result.hit_count.to_string(), display="inline")],
                    bg="#0F3020", color=GREEN,
                ),
                _badge(
                    [rx.text("Tasa: ", display="inline"),
                     rx.text(result.fault_pct.to_string(), display="inline"),
                     rx.text("%", display="inline")],
                    bg=BG_CARD2, color=TEXT2,
                ),
                gap="8px",
                flex_wrap="wrap",
                align="center",
            ),
            justify="between",
            align="center",
            flex_wrap="wrap",
            gap="10px",
            margin_bottom="16px",
        ),
        rx.box(
            rx.table.root(
                rx.table.body(
                    rx.foreach(result.table_rows, render_row),
                ),
                width="max-content",
                font_family=MONO,
                font_size="13px",
            ),
            overflow_x="auto",
            width="100%",
            padding_bottom="4px",
        ),
        # kwargs al final
        margin_bottom="14px",
        **CARD_STYLE,
    )


# ─── Panel de comparación ────────────────────────────────────────────────────

def _compare_bar(result: AlgoResult) -> rx.Component:
    return rx.hstack(
        rx.text(
            result.name,
            font_size="12px",
            color=TEXT2,
            min_width="170px",
            text_align="right",
            white_space="nowrap",
        ),
        rx.box(
            rx.box(
                width=result.fault_pct.to_string() + "%",
                height="100%",
                background=result.color,
                border_radius="3px",
            ),
            flex="1",
            height="20px",
            background=BG_CARD2,
            border_radius="3px",
            overflow="hidden",
            border=f"1px solid {BORDER}",
            min_width="80px",
        ),
        rx.hstack(
            rx.text(result.fault_count.to_string(), font_family=MONO, font_size="12px", color=RED),
            rx.text(" F / ", font_family=MONO, font_size="12px", color=TEXT2),
            rx.text(result.total.to_string(), font_family=MONO, font_size="12px", color=TEXT),
            spacing="0",
        ),
        spacing="3",
        align="center",
        width="100%",
    )


def comparison_panel() -> rx.Component:
    return rx.box(
        rx.text("Comparación — fallos de página", margin_bottom="16px", **LABEL_STYLE),
        rx.vstack(
            rx.foreach(PageState.results, _compare_bar),
            spacing="3",
            width="100%",
        ),
        # kwargs al final
        margin_bottom="24px",
        **CARD_STYLE,
    )
