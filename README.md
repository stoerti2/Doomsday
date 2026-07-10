# ☠️ DOOMSDAY - The Internet Port Scanner

## 👨‍💻 About the Author

This project was built by an experienced IT professional with decades of hands-on work in network security, infrastructure, and software development. 
At 55, I am actively seeking new opportunities—whether as a full-time employee, freelancer, or project collaborator. 
If you value experience, deep technical knowledge, and a no-nonsense approach to problem-solving, let's connect.

📫 I am open to job offers worldwide.  
✉️ **Contact**: [klaus@schloss-buskow.de]


**DOOMSDAY** is a powerful, no-nonsense network scanner for huge networks.

It systematically scans every IPv4 address in every /24 network block—from `1.0.0.0` to `254.255.255.0`—targeting the `.1` and `.254` addresses 
(typically routers, firewalls, and gateways) on a configurable set of ports.

---

## ⚡ Features

- **Full Internet Coverage**: Scans all public IPv4 /24 networks (`.1` and `.254` only).
- **Configurable Ports**: Edit the port list directly in `genDB.py` to target any TCP services.
- **SQLite-Powered**: Uses a lightweight, sharded database architecture for maximum efficiency.
- **Randomized Scanning**: Scans networks and IPs in random order to avoid detection and ensure fair coverage.
- **Resumable**: Already scanned entries are deleted from the database, so you can stop and restart anytime.
- **Lightning Fast**: Multi-threaded design scans thousands of targets per second.

---

## 📁 Project Structure
doomsday/

├── genDB.py # Database generator - creates all SQLite databases

├── scanner.py # Main scanner - scans targets and logs open ports

├── scan_dbs/ # Directory containing all generated SQLite databases

│ ├── 001/ # First octet directories (001-254)

│ │ ├── 000.db # Second octet databases (000-255)

│ │ ├── 001.db

│ │ └── ...

│ └── ...

└── offene_ports.txt # Output file containing all discovered open ports


---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- SQLite3 (bundled with Python)

### Clone & Setup

```bash
git clone https://github.com/yourusername/doomsday.git
cd doomsday
chmod +x genDB.py scanner.py

🛠️ Usage
Step 1: Generate the Databases
Before scanning, you must generate the SQLite databases that contain all target IPs and ports.

bash
python3 genDB.py
What this does:

Creates a directory structure scan_dbs/XXX/YYY.db for every /24 network.

Each database contains all .1 and .254 IPs combined with every port from the PORTS list.

Warning: This process generates ~65,000 databases and can take several hours to complete.

Customizing Ports:
Edit the PORTS list in genDB.py to change which ports are scanned:

python
# Default ports (you can add or remove any TCP port)
PORTS = [21, 22, 23, 80, 443, 8080, 8443, 2222, 3389, 5900, 3306, 1433, 8069, 9090]
Step 2: (Optional) Remove Private Networks
The generator includes all IPv4 space, including private ranges. If you only want to scan public IPs, delete the following directories:

bash
rm -rf scan_dbs/010/   # 10.0.0.0/8
rm -rf scan_dbs/172/   # 172.16.0.0/12
rm -rf scan_dbs/192/   # 192.168.0.0/16
Step 3: Start the Scanner
bash
python3 scanner.py
What this does:

Randomly selects a database and reads a batch of entries.

Scans each target IP:port combination.

Writes any open ports to offene_ports.txt in real-time.

Deletes scanned entries from the database to avoid duplicates.

Deletes empty databases automatically.

⚠️ Important: The output file offene_ports.txt is truncated (emptied) every time the scanner starts.
If you want to keep previous results, rename or back them up before running.

📊 Output Format
offene_ports.txt contains one open port per line in the format:

text
IP_ADDRESS:PORT
Example:

text
192.168.1.1:80
192.168.1.1:443
10.0.0.1:22
8.8.8.8:53
🔧 Configuration Options
Variable	Description	Default
PORTS	List of TCP ports to scan	See genDB.py
MAX_WORKERS	Number of concurrent threads	200
BATCH_SIZE	Entries to read per database	100
TIMEOUT	Connection timeout in seconds	1.0
These can be adjusted at the top of scanner.py.

🧠 How It Works
Database Generation (genDB.py)

Iterates over all /24 networks (1.0.0.0/24 to 254.255.255.0/24).

For each network, creates a SQLite database containing .1 and .254 IPs and all ports.

Saves each database in a hierarchical directory structure for performance.

Scanning (scanner.py)

Lists all existing databases and shuffles them randomly.

For each database, reads a random batch of entries.

Spawns threads to scan each IP:port combination.

On success, appends the result to offene_ports.txt.

Deletes scanned entries and removes empty databases.

⚠️ Disclaimer
DOOMSDAY is a powerful tool intended for:

Security researchers auditing their own networks.

System administrators checking for exposed services.

Educational purposes only.

Do not use this tool against systems you do not own or have explicit permission to test.
Unauthorized scanning is illegal in many jurisdictions and may be considered a hostile act.
The author assumes no responsibility for misuse.

📜 License
MIT License - Use at your own risk.

🙏 Contributing
Pull requests and issues are welcome. If you find a bug or have a feature request, please open an issue.

