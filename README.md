# chatroom-project

## Networking Overview

| Layer       | Protocol                  | Our Chat App Usage                                |
| ----------- | ------------------------- | ------------------------------------------------- |
| Application | JSON over custom protocol | Chat message structure (type, sender, etc.)       |
| Transport   | TCP                       | Reliable socket connection (`socket.SOCK_STREAM`) |
| Network     | IP                        | Uses `127.0.0.1` or LAN IP to connect clients     |
| Link        | Ethernet/Wi-Fi            | Managed by OS/hardware                            |

## Architecture Diagram

[ GUI ] -> [ JSON Message ] -> [ TCP Socket (SOCK_STREAM) ] -> [ IP Packet ] -> [ Wi-Fi / Ethernet ]

## Set Up
### Install required packages
```bash
pip install -r requirements.txt
```

### Create necessary **init**.py files (if not in repo) (for Mac)
```bash
touch __init__.py
touch shared/__init__.py
touch server/__init__.py
touch client/__init__.py
```

### Create necessary **init**.py files (if not in repo) (for Win)
```bash
type nul > __init__.py
type nul > shared\__init__.py
type nul > server\__init__.py
type nul > client\__init__.py
```

## Running the Application

### **IMPORTANT: Always run from the project root directory!**

```bash
# Make sure you're in the project root
cd /path/to/chatroom-project

# Activate your environment first
conda activate chatroom-env
# OR for virtual env:
# source chatroom-env/bin/activate  (Mac/Linux)
# chatroom-env\Scripts\activate     (Windows)
```

### Start the Server

```bash
python -m server.server
```

### Start the Client

```bash
python -m client.client
```

### For any other modules

```bash
python -m folder.filename
# Example: python -m utils.helper
```

## Common Issues & Solutions

### "ModuleNotFoundError: No module named 'shared'"

- **Cause**: Running from wrong directory or missing `__init__.py` files
- **Solution**:
  1. Make sure you're in the project root directory
  2. Use `python -m module.file` format instead of `python path/file.py`
  3. Ensure all `__init__.py` files exist

### "No module named 'server.server'"

- **Cause**: Missing `__init__.py` in server folder or running from wrong directory
- **Solution**: Create `server/__init__.py` and run from project root

### Environment not activating

- **Conda**: Try `conda init` then restart terminal
- **Virtual env**: Make sure you created it with the correct Python version
