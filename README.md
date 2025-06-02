# chatroom-project

## Networking Overview

| Layer       | Protocol                  | Our Chat App Usage                                |
| ----------- | ------------------------- | ------------------------------------------------- |
| Application | JSON over custom protocol | Chat message structure (type, sender, etc.)       |
| Transport   | TCP                       | Reliable socket connection (`socket.SOCK_STREAM`) |
| Network     | IP                        | Uses `127.0.0.1` or LAN IP to connect clients     |
| Link        | Ethernet/Wi-Fi            | Managed by OS/hardware                            |

## Architecture Diagram

[ GUI ]
↓
[ JSON Message ]
↓
[ TCP Socket (SOCK_STREAM) ]
↓
[ IP Packet ]
↓
[ Wi-Fi / Ethernet ]
