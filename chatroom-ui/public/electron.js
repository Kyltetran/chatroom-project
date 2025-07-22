const { ipcMain, app, BrowserWindow } = require("electron");
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

  // Optionally spawn client.py immediately (without username)
  const clientPath = path.resolve(__dirname, "../../client/client.py");

  clientProcess = spawn("python3", [clientPath], {
    cwd: path.resolve(__dirname, ".."), // Set working dir to project root
  });

  clientProcess.stdout.on("data", (data) => {
    console.log(`[client.py] ${data}`);
  });

  clientProcess.stderr.on("data", (data) => {
    console.error(`[client.py ERROR] ${data}`);
  });

  clientProcess.on("close", (code) => {
    console.log(`[client.py] Exited with code ${code}`);
    clientProcess = null;
  });
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    if (clientProcess) clientProcess.kill();
    app.quit();
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// ✅ Optional: spawn client with username from React app
ipcMain.on("start-client", (event, username) => {
  if (clientProcess) return;

  const clientPath = path.resolve(__dirname, "../../client/client.py");

  clientProcess = spawn("python3", [clientPath, username], {
    cwd: path.resolve(__dirname, ".."),
  });

  clientProcess.stdout.on("data", (data) => {
    console.log(`[client.py] ${data}`);
  });

  clientProcess.stderr.on("data", (data) => {
    console.error(`[client.py ERROR] ${data}`);
  });

  clientProcess.on("close", (code) => {
    console.log(`[client.py] Exited with code ${code}`);
    clientProcess = null;
  });
});
