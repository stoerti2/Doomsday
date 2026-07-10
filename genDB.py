#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import random
from concurrent.futures import ThreadPoolExecutor

# Ports (die gleichen wie beim Scanner)
ADMIN_PORTS = [21, 22, 23, 80, 443, 8080, 8443, 2222, 3389, 5900, 3306, 1433, 8069, 9090]

# Basisverzeichnis
DB_BASE = "scan_dbs"

def create_db_for_network(a, b):
    """
    Erstellt eine SQLite-Datenbank für das /16-Netz a.b.0.0/16.
    Speichert sie in scan_dbs/a/b.db
    """
    # Verzeichnis für 'a' erstellen
    dir_path = os.path.join(DB_BASE, f"{a:03d}")
    os.makedirs(dir_path, exist_ok=True)
    
    db_path = os.path.join(dir_path, f"{b:03d}.db")
    
    # Datenbank erstellen
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            port INTEGER NOT NULL,
            ip_port TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Daten einfügen (.1 und .254 für alle c in 0..255)
    targets = []
    for c in range(0, 256):
        for suffix in (1, 254):
            ip = f"{a}.{b}.{c}.{suffix}"
            for port in ADMIN_PORTS:
                ip_port = f"{ip}:{port}"
                targets.append((ip, port, ip_port))
    
    cursor.executemany(
        'INSERT OR IGNORE INTO targets (ip, port, ip_port) VALUES (?, ?, ?)',
        targets
    )
   
    conn.commit()
    conn.close()

def create_all_dbs():
    """Erstellt alle Datenbanken in hierarchischer Struktur."""
    os.makedirs(DB_BASE, exist_ok=True)
    
    total = 254 * 256  # 65.024
    print(f"[+] Erstelle {total} Datenbanken...")
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for a in range(1, 255):
            for b in range(0, 256):
                futures.append(executor.submit(create_db_for_network, a, b))
        
        for i, future in enumerate(futures):
            future.result()
            if (i + 1) % 1000 == 0:
                print(f"  Fortschritt: {i+1}/{total}")

def get_db_stats():
    """Zeigt Statistiken über die erstellten Datenbanken an."""
    total_dbs = 0
    total_size = 0
    
    for root, dirs, files in os.walk(DB_BASE):
        for f in files:
            if f.endswith('.db'):
                total_dbs += 1
                total_size += os.path.getsize(os.path.join(root, f))
    
    print(f"\n[+] Statistiken:")
    print(f"  Anzahl Datenbanken: {total_dbs}")
    print(f"  Gesamtgröße: {total_size / (1024**3):.2f} GB")
    print(f"  Durchschnitt pro DB: {total_size / total_dbs / (1024**2):.1f} MB")

if __name__ == "__main__":
    create_all_dbs()
    get_db_stats()
