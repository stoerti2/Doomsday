#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import socket
import sqlite3
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

DB_BASE = "scan_dbs"
OUTPUT_FILE = "offene_ports.txt"
TIMEOUT = 1.0
MAX_WORKERS = 200
BATCH_SIZE = 100

def get_all_db_paths():
    """Gibt alle vorhandenen .db-Dateien mit vollständigem Pfad zurück."""
    db_paths = []
    for root, dirs, files in os.walk(DB_BASE):
        for f in files:
            if f.endswith('.db'):
                db_paths.append(os.path.join(root, f))
    return db_paths

def get_random_dbs():
    """Gibt eine zufällig gemischte Liste aller Datenbankpfade zurück."""
    paths = get_all_db_paths()
    random.shuffle(paths)
    return paths

def get_random_entries(db_path, count):
    """Liest zufällige Einträge aus einer Datenbank."""
    entries = []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f'SELECT ip_port FROM targets ORDER BY RANDOM() LIMIT {count}')
        entries = [row[0] for row in cursor.fetchall()]
        conn.close()
    except Exception as e:
        print(f"  Fehler beim Lesen von {db_path}: {e}")
    return entries

def delete_entries(db_path, entries):
    """Löscht die angegebenen Einträge aus der Datenbank."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for entry in entries:
            cursor.execute('DELETE FROM targets WHERE ip_port = ?', (entry,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"  Fehler beim Löschen in {db_path}: {e}")

def delete_db_if_empty(db_path):
    """Löscht die Datenbank, wenn sie keine Einträge mehr enthält."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM targets')
        count = cursor.fetchone()[0]
        conn.close()
        
        if count == 0:
            os.remove(db_path)
            # Auch leere Verzeichnisse aufräumen (optional)
            dir_path = os.path.dirname(db_path)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
            return True
    except Exception:
        pass
    return False

def scan_target(target_str):
    try:
        ip, port_str = target_str.split(':')
        port = int(port_str)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIMEOUT)
            if sock.connect_ex((ip, port)) == 0:
                return target_str
    except Exception:
        pass
    return None

def main():
    print("=" * 80)
    print("  SQLite-Shuffle-Scanner (hierarchische Verzeichnisse)")
    print("=" * 80)
    
    if not os.path.exists(DB_BASE):
        print(f"[!] Verzeichnis {DB_BASE} nicht gefunden!")
        sys.exit(1)
    
    total_scanned = 0
    found = 0
    start_time = time.time()
    db_counter = 0
    
    with open(OUTPUT_FILE, 'w') as out_f:
        # Alle Datenbanken ermitteln und mischen
        dbs = get_random_dbs()
        total_dbs = len(dbs)
        
        for db_path in dbs:
            db_counter += 1
            print(f"\n[{db_counter}/{total_dbs}] Verarbeite: {db_path}")
            
            # Einträge aus der DB lesen
            entries = get_random_entries(db_path, BATCH_SIZE)
            if not entries:
                # DB ist leer – löschen
                os.remove(db_path)
                print(f"  DB leer, gelöscht.")
                continue
            
            # Scannen
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = {executor.submit(scan_target, e): e for e in entries}
                open_entries = []
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        open_entries.append(result)
                        found += 1
                        out_f.write(f"{result}\n")
                        out_f.flush()
                        print(f"[+] {result}  -> OFFEN  (Total: {found})")
            
            # Gescannte Einträge löschen
            delete_entries(db_path, entries)
            total_scanned += len(entries)
            
            # Prüfen, ob DB leer ist
            if delete_db_if_empty(db_path):
                print(f"  DB jetzt leer und gelöscht.")
            
            # Fortschritt
            elapsed = time.time() - start_time
            rate = total_scanned / elapsed if elapsed > 0 else 0
            remaining_dbs = len(get_all_db_paths())
            print(f"  Fortschritt: {total_scanned} gescannt, {found} offen, "
                  f"{remaining_dbs} DBs übrig, {rate:.1f} Ziele/s, "
                  f"Laufzeit: {elapsed/60:.1f} min", end='\r')
    
    print("\n\n" + "=" * 80)
    print("  ZUSAMMENFASSUNG")
    print("=" * 80)
    print(f"  Gescannte Ziele: {total_scanned}")
    print(f"  Offene Ports:    {found}")
    print(f"  Dauer:           {time.time() - start_time:.1f} s")
    print(f"  Ausgabe:         {OUTPUT_FILE}")
    print("=" * 80)
 
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Abbruch durch Benutzer.")
        sys.exit(0)
