import { Viewer } from './viewer.js';
import { api } from './api.js';
import * as ui from './ui.js';
import * as dialogs from './dialogs.js';
import { renderFileList } from './files.js';
import { LiveSync } from './live.js';

const app = {
  payload: null,
  files: [],
  filter: '',
  sort: 'name',
  viewer: null,
  busy: false,
};

let live = null;
let pendingLive = null;
let applyToken = 0;

const history = [];
let historyIndex = -1;

function updateActions() {
  ui.setActions({
    hasFile: Boolean(app.payload),
    dirty: Boolean(app.payload?.dirty),
    busy: app.busy,
  });
}

function renderFiles() {
  renderFileList(ui.els.fileList, app.files, {
    filter: app.filter,
    sort: app.sort,
    activeName: app.payload?.name ?? null,
    dirty: Boolean(app.payload?.dirty),
    onLoad: loadFile,
    onRename: renameFile,
    onDuplicate: duplicateFile,
    onDownload: (name) => {
      window.location.href = api.downloadUrl(name);
    },
    onDelete: deleteFile,
  });
}

async function refreshFiles() {
  const data = await api.files();
  app.files = data.files;
  ui.setFileCount(data.files.length);
  renderFiles();
}

async function applyState(payload, reframe = true) {
  const token = ++applyToken;
  app.payload = payload;
  if (live && Number.isFinite(payload?.revision)) live.noteRevision(payload.revision);
  if (!payload) {
    app.viewer.clear();
    ui.showEmpty();
    ui.els.viewSelect.value = 'iso';
  } else {
    ui.showLoaded(payload);
    if (!app.busy) ui.setStatus('构建模型…');
    try {
      await app.viewer.setModel(payload, reframe);
    } catch (error) {
      ui.toast(error.message || String(error), 'error');
    }
    if (token !== applyToken) return;
    window.__appliedState = {
      name: payload.name,
      revision: payload.revision,
      blockCount: payload.blockCount,
      at: Date.now(),
    };
    if (!app.busy) ui.setStatus('就绪');
    ui.els.viewSelect.value = app.viewer.viewMode || 'iso';
  }
  updateActions();
  renderFiles();
}

async function applyLive(data) {
  if (Array.isArray(data.files)) {
    app.files = data.files;
    ui.setFileCount(data.files.length);
  }
  const previous = app.payload;
  const previousRevision = previous?.revision ?? -1;
  if (data.state === null) {
    if (previous) await applyState(null, false);
    else renderFiles();
  } else if (!previous || data.state.revision > previousRevision) {
    const sizeChanged = !previous
      || previous.width !== data.state.width
      || previous.height !== data.state.height
      || previous.length !== data.state.length;
    await applyState(data.state, sizeChanged);
  } else {
    renderFiles();
  }
  if (data.actor === 'agent') ui.toast('AI 已更新');
}

function handleLive(data) {
  if (app.busy) {
    pendingLive = data;
    return;
  }
  applyLive(data).catch((error) => ui.toast(error.message || String(error), 'error'));
}

function flushLive() {
  if (!pendingLive) return;
  const data = pendingLive;
  pendingLive = null;
  const current = app.payload?.revision ?? -1;
  if (data.revision > current) {
    applyLive(data).catch((error) => ui.toast(error.message || String(error), 'error'));
  } else if (Array.isArray(data.files)) {
    app.files = data.files;
    ui.setFileCount(data.files.length);
    renderFiles();
  }
}

async function withBusy(text, task) {
  if (app.busy) return undefined;
  app.busy = true;
  ui.setBusy(true, text);
  updateActions();
  try {
    return await task();
  } catch (error) {
    ui.toast(error.message || String(error), 'error');
    return undefined;
  } finally {
    app.busy = false;
    ui.setBusy(false);
    updateActions();
    flushLive();
  }
}

async function loadFile(name) {
  await withBusy(`载入 ${name}…`, async () => {
    const data = await api.load(name);
    await applyState(data.state, true);
    await refreshFiles();
    ui.setLog(`已载入 ${name}`);
    ui.toast(`已载入 ${name}`);
  });
}

function createNew() {
  if (app.busy) return;
  dialogs.openForm({
    title: '新建空白投影',
    fields: [
      { name: 'name', label: '文件名', value: 'untitled.schem' },
      { name: 'width', label: '宽 X', type: 'number', value: '16', min: 1, max: 256, inline: true },
      { name: 'height', label: '高 Y', type: 'number', value: '16', min: 1, max: 256, inline: true },
      { name: 'length', label: '长 Z', type: 'number', value: '16', min: 1, max: 256, inline: true },
      { name: 'large', label: '128 × 128 × 128 大型画布', type: 'checkbox', value: false, required: false },
      { name: 'huge', label: '256 × 256 × 256 超大画布', type: 'checkbox', value: false, required: false },
    ],
    submitText: '创建',
    onSubmit: async (values) => {
      const size = values.huge ? 256 : values.large ? 128 : null;
      const data = await api.newFile({
        name: values.name,
        width: size ?? Number(values.width),
        height: size ?? Number(values.height),
        length: size ?? Number(values.length),
      });
      await applyState(data.state, true);
      await refreshFiles();
      ui.setLog(`已创建 ${data.state.name}`);
      ui.toast('已创建');
    },
  });
}

function renameFile(name) {
  if (app.busy) return;
  dialogs.openForm({
    title: '重命名投影',
    description: name,
    fields: [{ name: 'name', label: '新文件名', value: name }],
    submitText: '重命名',
    onSubmit: async (values) => {
      const data = await api.rename(name, values.name);
      await applyState(data.state, false);
      await refreshFiles();
      ui.toast('已重命名');
    },
  });
}

function duplicateFile(name) {
  if (app.busy) return;
  const base = name.replace(/\.schem$/i, '');
  dialogs.openForm({
    title: '复制投影',
    description: name,
    fields: [{ name: 'name', label: '新文件名', value: `${base}_copy.schem` }],
    submitText: '复制',
    onSubmit: async (values) => {
      await api.duplicate(name, values.name);
      await refreshFiles();
      ui.toast('已复制');
    },
  });
}

async function deleteFile(name) {
  if (app.busy) return;
  const active = app.payload?.name === name;
  const message = active && app.payload?.dirty
    ? `${name} 有未保存修改，删除后无法恢复。`
    : `删除 ${name}？此操作无法恢复。`;
  const ok = await dialogs.openConfirm({
    title: '删除投影',
    message,
    confirmText: '删除',
    danger: true,
  });
  if (!ok) return;
  await withBusy('删除中…', async () => {
    const data = await api.deleteFile(name);
    await applyState(data.state, false);
    await refreshFiles();
    ui.toast('已删除');
  });
}

async function save() {
  await withBusy('保存中…', async () => {
    const data = await api.save();
    await applyState(data.state, false);
    await refreshFiles();
    ui.toast('已保存到原文件');
  });
}

function saveAs() {
  if (!app.payload || app.busy) return;
  const base = app.payload.name.replace(/\.schem$/i, '');
  dialogs.openForm({
    title: '另存为',
    fields: [
      { name: 'name', label: '文件名', value: `${base}_out.schem` },
      { name: 'overwrite', label: '覆盖同名文件', type: 'checkbox', value: false, required: false },
    ],
    submitText: '保存',
    onSubmit: async (values) => {
      const data = await api.saveAs(values.name, values.overwrite);
      await applyState(data.state, false);
      await refreshFiles();
      ui.toast('已保存');
    },
  });
}

async function resetFile() {
  if (!app.payload || app.busy) return;
  if (app.payload.dirty) {
    const ok = await dialogs.openConfirm({
      title: '重置投影',
      message: '放弃未保存修改，恢复到原文件？',
      confirmText: '重置',
      danger: true,
    });
    if (!ok) return;
  }
  await withBusy('重置中…', async () => {
    const data = await api.reset();
    await applyState(data.state, false);
    ui.toast('已重置');
  });
}

async function closeFile() {
  if (!app.payload || app.busy) return;
  if (app.payload.dirty) {
    const ok = await dialogs.openConfirm({
      title: '关闭投影',
      message: '有未保存修改，确定关闭？',
      confirmText: '关闭',
      danger: true,
    });
    if (!ok) return;
  }
  await withBusy('关闭中…', async () => {
    const data = await api.close();
    await applyState(data.state, false);
    await refreshFiles();
    ui.toast('已关闭');
  });
}

async function run() {
  if (!app.payload || app.busy) return;
  const text = ui.els.commands.value.trim();
  if (!text) {
    ui.setLog('请输入 WorldEdit 命令', true);
    return;
  }
  if (history[history.length - 1] !== text) {
    history.push(text);
    if (history.length > 50) history.shift();
    historyIndex = -1;
  }

  app.busy = true;
  ui.setBusy(true, 'WorldEdit 正在执行…');
  ui.setStatus('运行中');
  updateActions();
  try {
    const data = await api.runRaw(text);
    if (data.log) ui.setLog(data.log);
    if (data.state) await applyState(data.state, false);
    if (!data.ok) {
      ui.setStatus('错误', true);
      if (data.error) {
        ui.setLog(`${data.log ? `${data.log}\n\n` : ''}${data.error}`, true);
        ui.toast(data.error, 'error');
      }
    } else {
      ui.setStatus('就绪');
      ui.toast('执行完成');
    }
  } catch (error) {
    ui.setStatus('错误', true);
    ui.setLog(`执行失败：${error.message}`, true);
    ui.toast(error.message, 'error');
  } finally {
    app.busy = false;
    ui.setBusy(false);
    updateActions();
    renderFiles();
    flushLive();
  }
}

async function uploadFile(file) {
  if (!file || app.busy) return;
  if (!file.name.toLowerCase().endsWith('.schem')) {
    ui.toast('只支持 .schem 文件', 'error');
    return;
  }
  await withBusy(`上传 ${file.name}…`, async () => {
    const buffer = await file.arrayBuffer();
    const data = await api.upload(file.name, buffer);
    await applyState(data.state, true);
    await refreshFiles();
    ui.setLog(`已上传 ${data.state.name}`);
    ui.toast('已上传');
  });
}

async function openFolder() {
  try {
    await api.reveal();
    ui.toast('已打开 schematics/');
  } catch (error) {
    ui.toast(error.message, 'error');
  }
}

function fillExample() {
  if (!app.payload) return;
  const { width, height, length } = app.payload;
  ui.els.commands.value = [
    '//pos1 0,0,0',
    `//pos2 ${width - 1},${height - 1},${length - 1}`,
    '//set minecraft:stone',
  ].join('\n');
}

function bindEvents() {
  ui.els.newBtn.addEventListener('click', createNew);
  ui.els.uploadBtn.addEventListener('click', () => ui.els.fileInput.click());
  ui.els.fileInput.addEventListener('change', () => {
    const [file] = ui.els.fileInput.files;
    ui.els.fileInput.value = '';
    uploadFile(file);
  });
  ui.els.refreshBtn.addEventListener('click', () => withBusy('刷新中…', refreshFiles));
  ui.els.revealBtn.addEventListener('click', openFolder);
  ui.els.fileSearch.addEventListener('input', () => {
    app.filter = ui.els.fileSearch.value;
    renderFiles();
  });
  ui.els.fileSort.addEventListener('change', () => {
    app.sort = ui.els.fileSort.value;
    renderFiles();
  });
  ui.els.runBtn.addEventListener('click', run);
  ui.els.saveBtn.addEventListener('click', save);
  ui.els.saveAsBtn.addEventListener('click', saveAs);
  ui.els.downloadBtn.addEventListener('click', () => {
    if (app.payload) window.location.href = api.downloadUrl();
  });
  ui.els.resetBtn.addEventListener('click', resetFile);
  ui.els.closeBtn.addEventListener('click', closeFile);
  ui.els.exampleBtn.addEventListener('click', fillExample);
  ui.els.fitBtn.addEventListener('click', () => setView('iso'));
  ui.els.viewSelect.addEventListener('change', () => setView(ui.els.viewSelect.value));
  ui.els.shotBtn.addEventListener('click', captureShot);
  ui.els.commands.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      run();
      return;
    }
    if (event.key === 'ArrowUp' && ui.els.commands.value.trim() === '' && history.length) {
      event.preventDefault();
      historyIndex = Math.max(0, historyIndex < 0 ? history.length - 1 : historyIndex - 1);
      ui.els.commands.value = history[historyIndex];
    } else if (event.key === 'ArrowDown' && historyIndex >= 0) {
      event.preventDefault();
      historyIndex += 1;
      if (historyIndex >= history.length) {
        historyIndex = -1;
        ui.els.commands.value = '';
      } else {
        ui.els.commands.value = history[historyIndex];
      }
    }
  });

  let dragDepth = 0;
  ui.els.main.addEventListener('dragenter', (event) => {
    event.preventDefault();
    dragDepth += 1;
    ui.els.dropHint.classList.remove('hidden');
  });
  ui.els.main.addEventListener('dragover', (event) => event.preventDefault());
  ui.els.main.addEventListener('dragleave', () => {
    dragDepth = Math.max(0, dragDepth - 1);
    if (dragDepth === 0) ui.els.dropHint.classList.add('hidden');
  });
  ui.els.main.addEventListener('drop', (event) => {
    event.preventDefault();
    dragDepth = 0;
    ui.els.dropHint.classList.add('hidden');
    const [file] = event.dataTransfer.files;
    uploadFile(file);
  });
}

function setView(mode) {
  app.viewer.setView(mode);
  ui.els.viewSelect.value = mode;
}

async function captureShot() {
  if (!app.payload) return;
  if (app.viewer.viewMode !== ui.els.viewSelect.value) {
    setView(ui.els.viewSelect.value);
  }
  try {
    const { png, meta } = app.viewer.capture();
    const stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\..+$/, '').replace('T', '-');
    const base = (app.payload.name || 'untitled')
      .replace(/\.schem$/i, '')
      .replace(/[^\w.-]+/g, '_');
    const data = await api.saveShot({
      name: `${base}_${meta.view}_${stamp}.png`,
      png,
      meta,
    });
    ui.toast(`截图已保存：${data.image}`);
    ui.setLog(`截图：${data.image}\n视角：${meta.view}\n机位：${JSON.stringify(meta.camera)}`);
  } catch (error) {
    ui.toast(error.message || String(error), 'error');
  }
}

async function boot() {
  app.viewer = new Viewer(ui.els.view, ui.els.main);
  app.viewer.onPick = (record) => {
    if (!record) {
      ui.setHudInfo('未选中方块');
      return;
    }
    ui.setHudInfo(`${record.name} @ (${record.x}, ${record.y}, ${record.z})`);
  };
  app.viewer.onProgress = (text) => {
    if (app.busy) ui.setBusyText(text);
    else ui.setStatus(text);
  };
  app.viewer.onNotice = (message) => ui.toast(message, 'error');
  app.viewer.onMetrics = (metrics) => {
    console.info('[render]', metrics);
    window.__renderMetrics = metrics;
  };
  live = new LiveSync({ onEvent: handleLive });
  bindEvents();
  ui.setActions({ hasFile: false, dirty: false, busy: false });
  try {
    await refreshFiles();
  } catch (error) {
    ui.toast(error.message, 'error');
  }
  try {
    const data = await api.state();
    if (Number.isFinite(data.revision)) live.noteRevision(data.revision);
    if (data.state) ui.setBusy(true, '加载模型…');
    try {
      await applyState(data.state, true);
    } finally {
      ui.setBusy(false);
      updateActions();
    }
  } catch (error) {
    await applyState(null, true);
    ui.toast(error.message, 'error');
  }
  live.start();
}

boot();
