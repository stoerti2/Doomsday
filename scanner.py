#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#┌────────────────────────────────────────────────────────────────────────┐
#│                                                                        │
#│         ███████╗████████╗ ██████╗ ███████╗██████╗ ████████╗██╗         │
#│         ██╔════╝╚══██╔══╝██╔═══██╗██╔════╝██╔══██╗╚══██╔══╝██║         │
#│         ███████╗   ██║   ██║   ██║█████╗  ██████╔╝   ██║   ██║         │
#│         ╚════██║   ██║   ██║   ██║██╔══╝  ██╔══██╗   ██║   ██║         │
#│         ███████║   ██║   ╚██████╔╝███████╗██║  ██║   ██║   ██║         │
#│         ╚══════╝   ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝         │
#│                                                                        │
#│                       "old school, still root"                         │
#│                    "stoerti - the jobless hacker"                      │
#│                                                                        │
#│    ┌──────────────────────────────────────────────────────────────┐    │
#│    │  40 years in the trenches.     │  6 months unemployed in DE. │    │
#│    │  They fired the one who knew.  │  This is my legacy.         │    │
#│    │                   -- no patches for reality --               │    │
#│    └──────────────────────────────────────────────────────────────┘    │
#│                                                                        │
#└────────────────────────────────────────────────────────────────────────┘
# =============================================================================
# MIT License
# =============================================================================
#
# Copyright (c) 2026 Klaus Baumdick
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# =============================================================================
# DISCLAIMER OF WARRANTY / USE AT YOUR OWN RISK
# =============================================================================
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# =============================================================================
# ADDITIONAL DISCLAIMER FOR CYBERSECURITY / OFFENSIVE TOOLS
# =============================================================================
#
# THIS SCRIPT IS INTENDED FOR LEGITIMATE SECURITY TESTING, EDUCATIONAL PURPOSES,
# AND AUTHORIZED PENETRATION TESTING ONLY.
#
# THE USER ASSUMES FULL RESPONSIBILITY FOR ANY AND ALL CONSEQUENCES RESULTING
# FROM THE USE OF THIS SCRIPT. THIS INCLUDES, BUT IS NOT LIMITED TO:
#   - LEGAL LIABILITY
#   - CIVIL OR CRIMINAL PROSECUTION
#   - DAMAGE TO SYSTEMS OR DATA
#   - VIOLATION OF LOCAL, NATIONAL, OR INTERNATIONAL LAWS
#
# BY USING THIS SCRIPT, YOU AGREE THAT YOU ARE SOLELY RESPONSIBLE FOR ENSURING
# THAT YOUR USE COMPLIES WITH ALL APPLICABLE LAWS AND REGULATIONS IN YOUR
# JURISDICTION. THE AUTHOR(S) AND COPYRIGHT HOLDER(S) ACCEPT NO RESPONSIBILITY
# OR LIABILITY FOR ANY MISUSE, ILLEGAL ACTIVITIES, OR DAMAGES CAUSED BY THIS
# SOFTWARE.
#
# YOU HAVE BEEN WARNED. USE THIS SCRIPT AT YOUR OWN RISK.
# =============================================================================
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
    """Gibt eine zufällig gemischte Liste aller vorhandenen Datenbankpfade zurück."""
    paths = get_all_db_paths()
    random.shuffle(paths)
    return paths

def get_random_entries(db_path, count):
    """Liest zufällige Einträge aus einer Datenbank.
    Gibt leere Liste zurück, falls die Datei nicht existiert oder nicht lesbar ist."""
    if not os.path.exists(db_path):
        return []  # Stabil: einfach überspringen
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
    """Löscht die angegebenen Einträge aus der Datenbank.
    Tut nichts, wenn die Datei nicht existiert."""
    if not os.path.exists(db_path):
        return
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
    """Löscht die Datenbank, wenn sie keine Einträge mehr enthält.
    Gibt True zurück, wenn die Datei gelöscht wurde, sonst False.
    Existiert die Datei nicht, wird False zurückgegeben (keine Aktion)."""
    if not os.path.exists(db_path):
        return False
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
        # Alle aktuell vorhandenen Datenbanken ermitteln und mischen
        dbs = get_random_dbs()
        total_dbs = len(dbs)

        for db_path in dbs:
            # Prüfen, ob die Datenbank noch existiert (kann extern gelöscht sein)
            if not os.path.exists(db_path):
                print(f"[!] Datenbank {db_path} nicht mehr vorhanden – überspringe.")
                continue

            db_counter += 1
            print(f"\n[{db_counter}/{total_dbs}] Verarbeite: {db_path}")

            # Einträge aus der DB lesen
            entries = get_random_entries(db_path, BATCH_SIZE)
            if not entries:
                # Wenn keine Einträge gelesen wurden: prüfen, ob DB leer ist und ggf. löschen
                if delete_db_if_empty(db_path):
                    print(f"  DB leer, gelöscht.")
                else:
                    print(f"  Keine Einträge lesbar oder DB bereits leer – überspringe.")
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

            # Prüfen, ob DB jetzt leer ist (und ggf. löschen)
            if delete_db_if_empty(db_path):
                print(f"  DB jetzt leer und gelöscht.")

            # Fortschritt anzeigen
            elapsed = time.time() - start_time
            rate = total_scanned / elapsed if elapsed > 0 else 0
            remaining_dbs = len(get_all_db_paths())  # aktuelle Anzahl der DBs
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

    # Prüfen, ob nach Verarbeitung aller ursprünglichen DBs keine mehr vorhanden sind
    if not get_all_db_paths():
        print("\n" + "=" * 80)
        print("  All databases processed. Please restart the scanner for the next round.")
        print("=" * 80)
    else:
        # Optionale Info, falls noch DBs übrig sind (z.B. weil neue hinzugekommen)
        # wird aber nicht explizit verlangt
        pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Abbruch durch Benutzer.")
        sys.exit(0)
