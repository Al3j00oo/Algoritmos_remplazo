import reflex as rx
from .state import PageState
from .components import (
    input_section, algo_selector, algo_table,
    comparison_panel, BG, BG_CARD, BORDER, TEXT, TEXT2, ACCENT, FONT, MONO,
)


def header() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.text("OS", font_size="10px", font_weight="700",
                                color=ACCENT, font_family=MONO),
                        background=f"{ACCENT}22",
                        border=f"1px solid {ACCENT}44",
                        border_radius="5px",
                        padding="2px 7px",
                    ),
                    rx.text(
                        "Simulador de Reemplazo de Paginas",
                        font_size="20px", font_weight="700",
                        color=TEXT, letter_spacing="-0.03em",
                    ),
                    spacing="3", align="center",
                ),
                rx.text(
                    "FIFO - Optimo - Segunda Oportunidad - LRU - MRU",
                    font_size="12px", color=TEXT2, font_family=MONO,
                ),
                align="start", spacing="1",
            ),
            justify="between",
            align="center",
            flex_wrap="wrap",
        ),
        background=BG_CARD,
        border_bottom=f"1px solid {BORDER}",
        padding="16px 32px",
        position="sticky",
        top="0",
        z_index="100",
        width="100%",
    )


def main_content() -> rx.Component:
    return rx.box(
        rx.box(
            input_section(),
            algo_selector(),
            rx.cond(
                PageState.ran,
                rx.vstack(
                    comparison_panel(),
                    rx.foreach(PageState.results, algo_table),
                    spacing="0",
                    width="100%",
                ),
                rx.box(),
            ),
            max_width="1100px",
            margin="0 auto",
            padding="28px 20px 60px",
        ),
    )


def footer() -> rx.Component:
    return rx.box(
        rx.text(
            "Sistemas Operativos - Simulador de Algoritmos de Reemplazo de Paginas",
            font_size="11px", color=TEXT2, text_align="center", font_family=MONO,
        ),
        border_top=f"1px solid {BORDER}",
        padding="14px",
        width="100%",
    )


def index() -> rx.Component:
    return rx.box(
        header(),
        main_content(),
        footer(),
        background=BG,
        min_height="100vh",
        font_family=FONT,
        color=TEXT,
    )


app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap"
    ],
)
app.add_page(index, route="/", title="Simulador - Reemplazo de Paginas")
