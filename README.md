# ☠️ DOOMSDAY - The Internet Port Scanner

## 👨‍💻 About the Author

This project was built by an experienced IT professional with decades of hands-on work in network security, 
infrastructure, and software development. 
At 55, I am actively seeking new opportunities—whether as a full-time employee, freelancer, or project collaborator. 
If you value experience, deep technical knowledge, and a no-nonsense approach to problem-solving, let's connect.

📫 I am open to job offers worldwide.  
✉️ **Contact**: [klaus@schloss-buskow.de]


**DOOMSDAY** is a powerful, no-nonsense network scanner for huge networks.

It systematically scans every IPv4 address in every /24 network block—from `1.0.0.0` to 
`254.255.255.0`—targeting the `.1` and `.254` addresses 
(typically routers, firewalls, and gateways) on a configurable set of ports.

---

## ⚡ Features

- **Full Internet Coverage**: Scans all public IPv4 /24 networks (`.1` and `.254` only as configured in genDB.py).
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

git clone https://github.com/stoerti2/doomsday.git

cd doomsday

chmod +x genDB.py scanner.py

🛠️ Usage
Step 1: Generate the Databases
Before scanning, you must generate the SQLite databases that contain all target IPs and ports.


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

The generator includes all IPv4 space, including private ranges.

If you only want to scan public IPs, delete the following directories:

rm -rf scan_dbs/010/     # 10.0.0.0/8

rm -rf scan_dbs/172/16   # 172.16.0.0/12

rm -rf scan_dbs/192/168  # 192.168.0.0/16


Step 3: Start the Scanner
bash
python3 scanner.py
What this does:

Randomly selects a database and reads a batch of entries.

Scans each target IP:port combination.

Writes any open ports to offene_ports.txt in real-time.

Deletes scanned entries from the database to avoid duplicates.

Deletes empty databases automatically.

⚠️ Important: The output file offene_ports.txt is truncated (emptied)
every time the scanner starts.
If you want to keep previous results, rename or back them up before running.

📊 Output Format
offene_ports.txt contains one open port per line in the format:

IP_ADDRESS:PORT
Example:

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

---
```text
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
```
## This is Grindware

What is Grindware?

Grindware is software that exists because nobody pays me to build the things that actually matter.

I've been unemployed for six months. Not because I can't code – but because the market doesn't care about skills anymore. It cares about buzzwords, certificates, and who you know. 
So instead of waiting for a job that never comes, I build.

Grindware is the result of that.

### The Philosophy Grindware is:

Built out of necessity – not for profit, not for investors, not for a product roadmap. Built because something needed to exist and nobody else was going to build it.

Released for free – because locking code behind a paywall feels wrong when you know what it's like to have nothing.

Honest – no marketing fluff, no "enterprise-grade" nonsense. Just code that works.

Unpolished but functional – it gets the job done. If you need a pretty UI, go somewhere else.

### Why "Grindware"?
Because that's what it is. Code written during the grind. During the late nights. During the 47th job rejection. During the moments when you realize that the system doesn't care about you, so you might as well build your own.

Grindware is survival code.

### Who is Grindware for?
Developers who are tired of corporate BS

Security researchers who need tools that actually work

Anyone who believes software should be useful, not just profitable

People who are also grinding

### What Grindware is NOT
Not a company

Not a startup

Not a product

Not for sale

Grindware is just code. From one unemployed developer to the world.

### Support Grindware
If you use Grindware, that's enough. If you want to support it, you can:

⭐ Star the repository

🐛 Report bugs

🔧 Contribute code

💬 Share it with someone who might need it

### Contact
I'm always open to work. If you need a developer who actually builds things, let's talk.

Grindware – Built in the grind, released for free.

## 📬 Contact

For questions or inquiries regarding this dataset, please contact klaus@schloss-buskow.de

---

**Last Updated:** July 2026


🙏 Contributing
Pull requests and issues are welcome. If you find a bug or have a feature request, please open an issue.

