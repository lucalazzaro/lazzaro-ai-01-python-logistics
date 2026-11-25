# LogiServe — Warehouse & Order Monitoring (Python)

> Progetto sviluppato nell'ambito del Master in AI Solution Architecture
> (ProfessionAI) — modulo Python. Caso di studio a fini didattici.

## Descrizione
A command-line application that simulates warehouse and order management for
LogiServe S.r.l., a fictional B2B e-commerce company distributing electrical
components. It registers incoming orders, checks stock availability, updates
inventory when orders are fulfilled, and produces a daily report. Data is
persisted to CSV (product catalogue) and JSON (orders).

## Stack
- Python 3, standard library only (`csv`, `json`, `datetime`, `os`)
- No external dependencies

## Skill dimostrate
- Program structure with clearly separated functions (inventory, orders, reporting, persistence)
- Reading and writing CSV and JSON data files
- Input validation and error handling in an interactive text menu
- Activity logging with timestamps and operator name
- Designing business logic around stock levels and reorder points

## Come eseguire
No installation required.

```bash
python LogiServe.py
```

On first run the program creates a `dati/` folder with a sample product
catalogue. It asks for an operator name, then shows a text menu.

## Note
- Caso di studio a fini didattici. I dati, le aziende e i contatti citati nel
  codice sono interamente fittizi.
- The `dati/` folder is generated at runtime and is not versioned.
