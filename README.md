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

## Development Workflow (For Mac using conda)

1. **Always activate your environment first**

   ```bash
   conda activate chatroom-env
   ```

2. **Navigate to project root**

   ```bash
   cd /path/to/chatroom-project
   ```

3. **Run your scripts using module format**

   ```bash
   python -m server.server
   python -m client.client
   ```

4. **Before committing, test that imports work**
   ```bash
   python -c "from shared.config import *; print('Imports working!')"
   ```
