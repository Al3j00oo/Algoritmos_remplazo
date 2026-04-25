# Simulador de Reemplazo de Páginas — Reflex

Implementación visual de los algoritmos clásicos de reemplazo de páginas para Sistemas Operativos.

## Algoritmos incluidos

| Algoritmo | Descripción |
|---|---|
| **FIFO** | Desaloja la página más antigua en memoria |
| **Óptimo (Bélády)** | Desaloja la que no se usará por más tiempo en el futuro |
| **Segunda Oportunidad** | FIFO mejorado con bit de referencia y puntero circular |
| **LRU** | Desaloja la usada hace más tiempo |
| **MRU** | Desaloja la usada más recientemente |

## Estructura del proyecto

```
page_replacement/
├── rxconfig.py
├── requirements.txt
├── README.md
└── page_replacement/
    ├── __init__.py
    ├── state.py          ← Lógica de algoritmos + Estado Reflex
    ├── components.py     ← Componentes de UI reutilizables
    └── page_replacement.py  ← Página principal + App
```

## Instalación y ejecución

```bash
# 1. Crear entorno virtual (recomendado)
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Inicializar Reflex (solo la primera vez)
reflex init

# 4. Ejecutar en modo desarrollo
reflex run
```

Abrir en el navegador: http://localhost:3000

## Lógica de fallos de página

Un **fallo de página** ocurre cuando la página referenciada **no está en ningún marco** en ese instante, sin importar si hay espacio libre o si los marcos están llenos. Siempre que entra una nueva página → fallo.

## Detalles de Segunda Oportunidad

La tabla muestra para cada paso:
- El estado de los **bits de referencia** por marco (`0` / `1`)
- La posición del **puntero circular** (`→M0`, `→M1`, …)

Cuando hay un acierto, el bit de referencia del marco correspondiente se activa a `1`.
Cuando hay un fallo, el algoritmo recorre desde el puntero: si bit=`1` lo pone a `0` y avanza; si bit=`0` desaloja esa página.
