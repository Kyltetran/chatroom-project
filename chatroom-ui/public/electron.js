const { app, BrowserWindow } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

let clientProcess = null;

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  win.loadFile(path.join(__dirname, "../build/index.html"));

  // Start Python client.py in the background
  const clientPath = "/Users/trngmtam/Code/chatroom-project/client/client.py";
  clientProcess = spawn("python3", [clientPath]);

  clientProcess.stdout.on("data", (data) => {
    console.log(`[client.py] ${data}`);
  });

  clientProcess.stderr.on("data", (data) => {
    console.error(`[client.py ERROR] ${data}`);
  });

  clientProcess.on("close", (code) => {
    console.log(`[client.py] Exited with code ${code}`);
  });
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    if (clientProcess) clientProcess.kill(); // ❌ Stop the background process
    app.quit();
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
