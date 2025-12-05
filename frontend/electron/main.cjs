const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process'); // 引入进程控制

// 定义全局变量，防止被垃圾回收
let pyProc = null;

// 启动 Python 后端的函数
function createPyProc() {
  let scriptPath;

  if (process.env.NODE_ENV === 'development') {
    // 开发模式：我们自己手动启动了Python，这里啥都不用做
    console.log('开发模式：请手动启动 Python 后端');
    return;
  } else {
    // 生产模式：启动打包进去的 exe 文件
    // process.resourcesPath 是软件安装后的资源目录
    scriptPath = path.join(process.resourcesPath, 'backend', 'main.exe');
    console.log('启动后端:', scriptPath);

    // 启动子进程
    pyProc = spawn(scriptPath);

    pyProc.stdout.on('data', (data) => {
      console.log('Python输出:', data.toString());
    });

    pyProc.stderr.on('data', (data) => {
      console.error('Python报错:', data.toString());
    });
  }
}

// 退出软件时，一定要杀掉 Python 进程，否则它会一直在后台跑
function exitPyProc() {
  if (pyProc) {
    pyProc.kill();
    pyProc = null;
  }
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    titleBarStyle: 'hidden',
    titleBarOverlay: { color: '#0f1014', symbolColor: '#ffffff', height: 30 },
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false
    }
  });

  if (process.env.NODE_ENV === 'development') {
    win.loadURL('http://localhost:5174');
  } else {
    // 打包后加载构建好的 HTML 文件
    win.loadFile(path.join(__dirname, '../dist/index.html'));
  }
}

app.whenReady().then(() => {
  createPyProc(); // 先启动后端
  createWindow(); // 再打开窗口
});

app.on('will-quit', exitPyProc); // 退出时清理进程