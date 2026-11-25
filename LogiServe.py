"""
Sistema di gestione magazzino e ordini per LogiServe S.r.l.

LogiServe vende componenti elettrici a officine e rivenditori. Il programma
permette di visualizzare il magazzino, registrare ordini, evaderli e
generare un report giornaliero. E' un programma testuale, da riga di comando.

Per avviarlo: python main.py
Al primo avvio viene creata la cartella "dati" con un catalogo prodotti e
un ordine di esempio, cosi' si puo' provare il programma da subito.
"""

import csv
import json
import os
from datetime import date, datetime

PRODUCTS_FILE = "dati/catalogo.csv"
ORDERS_FILE = "dati/ordini.json"
LOG_FILE = "dati/log.txt"

products = []
orders = []
operator_name = ""


def ensure_data_folder():
    """Create the data folder if it does not exist yet."""
    if not os.path.exists("dati"):
        os.makedirs("dati")


def load_products():
    """Load the product catalog from file, creating sample data on first run."""
    if not os.path.exists(PRODUCTS_FILE):
        sample_products = [
            ["P001", "Interruttore magnetotermico 16A", "Interruttori", "50", "10", "pz"],
            ["P002", "Cavo elettrico 2.5mm (rotolo 100m)", "Cavi", "20", "5", "rotolo"],
            ["P003", "Presa industriale 16A", "Prese", "30", "8", "pz"],
            ["P004", "Quadro elettrico 12 moduli", "Quadri", "15", "3", "pz"],
            ["P005", "Lampada LED da cantiere", "Illuminazione", "40", "10", "pz"],
        ]
        with open(PRODUCTS_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["code", "name", "category", "stock", "reorder_point", "unit"])
            for row in sample_products:
                writer.writerow(row)

    with open(PRODUCTS_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            row["stock"] = int(row["stock"])
            row["reorder_point"] = int(row["reorder_point"])
            products.append(row)


def save_products():
    """Save the product catalog to file."""
    with open(PRODUCTS_FILE, "w", newline="") as file:
        fields = ["code", "name", "category", "stock", "reorder_point", "unit"]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for product in products:
            writer.writerow(product)


def find_product(code):
    """Return the product dict with the given code, or None if not found."""
    for product in products:
        if product["code"].upper() == code.upper():
            return product
    return None


def check_availability(code, quantity):
    """Return 'disponibile', 'parziale' or 'indisponibile' for the requested quantity."""
    product = find_product(code)
    if product is None:
        return "indisponibile"
    if product["stock"] >= quantity:
        return "disponibile"
    elif product["stock"] > 0:
        return "parziale"
    return "indisponibile"


def show_inventory():
    """Print the list of products currently in the warehouse."""
    print("")
    for product in products:
        line = product["code"] + " - " + product["name"]
        line += " | giacenza: " + str(product["stock"]) + " " + product["unit"]
        line += " | punto di riordino: " + str(product["reorder_point"])
        if product["stock"] <= product["reorder_point"]:
            line += "  <-- sotto soglia, da riordinare"
        print(line)
    print("")


def load_orders():
    """Load the order list from file, creating a sample order on first run."""
    if not os.path.exists(ORDERS_FILE):
        sample_orders = [
            {
                "order_id": 1,
                "date": "2026-06-15",
                "customer": "Officina Rossi",
                "status": "in attesa",
                "items": [
                    {"code": "P001", "quantity": 5},
                    {"code": "P003", "quantity": 2}
                ]
            }
        ]
        with open(ORDERS_FILE, "w") as file:
            json.dump(sample_orders, file, indent=4)

    with open(ORDERS_FILE, "r") as file:
        loaded_orders = json.load(file)
        for order in loaded_orders:
            orders.append(order)


def save_orders():
    """Save the order list to file."""
    with open(ORDERS_FILE, "w") as file:
        json.dump(orders, file, indent=4)


def next_order_id():
    """Return the next available order id."""
    highest = 0
    for order in orders:
        if order["order_id"] > highest:
            highest = order["order_id"]
    return highest + 1


def find_order(order_id):
    """Return the order dict with the given id, or None if not found."""
    for order in orders:
        if order["order_id"] == order_id:
            return order
    return None


def register_order():
    """Ask the user for the order details and register a new order."""
    customer = input("Nome cliente: ")
    items = []
    adding = True

    while adding:
        code = input("Codice prodotto (es. P001): ")
        try:
            quantity = int(input("Quantita' richiesta: "))
        except ValueError:
            print("Quantita' non valida, riprova.")
            continue

        items.append({"code": code, "quantity": quantity})
        answer = input("Vuoi aggiungere un altro prodotto? (s/n): ")
        if answer.lower() != "s":
            adding = False

    for item in items:
        status = check_availability(item["code"], item["quantity"])
        print(item["code"] + ": " + status)

    order = {
        "order_id": next_order_id(),
        "date": str(date.today()),
        "customer": customer,
        "status": "in attesa",
        "items": items
    }
    orders.append(order)
    save_orders()

    print("Ordine #" + str(order["order_id"]) + " registrato.")
    write_log("nuovo_ordine", "ordine #" + str(order["order_id"]) + " registrato per " + customer)


def fulfill_order():
    """Ask for an order number and fulfill it if all the items are available."""
    try:
        order_id = int(input("Numero ordine da evadere: "))
    except ValueError:
        print("Numero ordine non valido.")
        return

    order = find_order(order_id)
    if order is None:
        print("Nessun ordine trovato con questo numero.")
        return

    if order["status"] == "evaso":
        print("Questo ordine e' gia' stato evaso.")
        return

    for item in order["items"]:
        if check_availability(item["code"], item["quantity"]) != "disponibile":
            print("Scorta non sufficiente per " + item["code"] + ", ordine non evaso.")
            return

    for item in order["items"]:
        product = find_product(item["code"])
        product["stock"] = product["stock"] - item["quantity"]

    order["status"] = "evaso"
    save_orders()
    save_products()

    print("Ordine #" + str(order_id) + " evaso.")
    write_log("evasione_ordine", "ordine #" + str(order_id) + " evaso")


def show_orders():
    """Print the list of orders, optionally filtered by status."""
    status_filter = input("Filtra per stato (in attesa/evaso, vuoto per tutti): ")
    print("")
    for order in orders:
        if status_filter and order["status"] != status_filter:
            continue
        print("Ordine #" + str(order["order_id"]) + " - " + order["date"] +
              " - cliente: " + order["customer"] + " - stato: " + order["status"])
        for item in order["items"]:
            print("     " + item["code"] + " x " + str(item["quantity"]))
    print("")


def daily_report():
    """Compute, print and save the daily report."""
    today = str(date.today())

    received_today = 0
    for order in orders:
        if order["date"] == today:
            received_today += 1

    fulfilled = 0
    pending = 0
    for order in orders:
        if order["status"] == "evaso":
            fulfilled += 1
        else:
            pending += 1

    sales = {}
    for order in orders:
        if order["status"] == "evaso":
            for item in order["items"]:
                code = item["code"]
                if code not in sales:
                    sales[code] = 0
                sales[code] = sales[code] + item["quantity"]
    best_sellers = sorted(sales.items(), key=lambda entry: entry[1], reverse=True)

    low_stock = []
    for product in products:
        if product["stock"] <= product["reorder_point"]:
            low_stock.append(product)

    lines = []
    lines.append("REPORT GIORNALIERO - LogiServe S.r.l.")
    lines.append("Data: " + today)
    lines.append("")
    lines.append("Ordini ricevuti oggi: " + str(received_today))
    lines.append("Ordini evasi (totale): " + str(fulfilled))
    lines.append("Ordini in attesa (totale): " + str(pending))
    lines.append("")
    lines.append("Prodotti piu' venduti:")
    if len(best_sellers) == 0:
        lines.append("  nessuna vendita registrata")
    else:
        for code, quantity in best_sellers[:3]:
            lines.append("  " + code + " - " + str(quantity) + " unita' vendute")
    lines.append("")
    lines.append("Prodotti sotto la soglia di riordino:")
    if len(low_stock) == 0:
        lines.append("  nessun prodotto sotto soglia")
    else:
        for product in low_stock:
            lines.append("  " + product["code"] + " - " + product["name"])

    report_text = "\n".join(lines)
    print("")
    print(report_text)

    report_file = "dati/report_" + today + ".txt"
    with open(report_file, "w") as file:
        file.write(report_text)

    write_log("report", "report giornaliero generato e salvato in " + report_file)


def write_log(action, detail):
    """Append a line with timestamp, operator, action and detail to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = timestamp + " | operatore: " + operator_name + " | " + action + " | " + detail
    with open(LOG_FILE, "a") as file:
        file.write(line + "\n")


def show_help():
    """Print the list of available commands."""
    print("")
    print("I comandi disponibili sono i seguenti:")
    print(" - magazzino: visualizza il magazzino")
    print(" - ordine: registra un nuovo ordine")
    print(" - evadi: evadi un ordine")
    print(" - ordini: visualizza gli ordini")
    print(" - report: genera il report giornaliero")
    print(" - aiuto: mostra i comandi disponibili")
    print(" - esci: esci dal programma")
    print("")


ensure_data_folder()
load_products()
load_orders()

print("Benvenuto nel sistema di gestione di LogiServe!")
operator_name = input("Inserisci il tuo nome (operatore): ")
show_help()

cmd = None
while cmd != "esci":
    cmd = input("Inserisci un comando: ")

    if cmd == "magazzino":
        show_inventory()
    elif cmd == "ordine":
        register_order()
    elif cmd == "evadi":
        fulfill_order()
    elif cmd == "ordini":
        show_orders()
    elif cmd == "report":
        daily_report()
    elif cmd == "aiuto":
        show_help()
    elif cmd == "esci":
        save_products()
        save_orders()
        write_log("chiusura", "sessione terminata")
        print("Arrivederci!")
    else:
        print("Comando non valido.")
        show_help()
