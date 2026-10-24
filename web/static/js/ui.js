export const els = {
  main: document.querySelector('#main'),
  view: document.querySelector('#view'),
  fileList: document.querySelector('#fileList'),
  fileCount: document.querySelector('#fileCount'),
  fileSearch: document.querySelector('#fileSearch'),
  fileSort: document.querySelector('#fileSort'),
  fileInput: document.querySelector('#fileInput'),
  newBtn: document.querySelector('#newBtn'),
  uploadBtn: document.querySelector('#uploadBtn'),
  refreshBtn: document.querySelector('#refreshBtn'),
  revealBtn: document.querySelector('#revealBtn'),
  emptyState: document.querySelector('#emptyState'),
  emptyUploadBtn: document.querySelector('#emptyUploadBtn'),
  emptyNewBtn: document.querySelector('#emptyNewBtn'),
  hud: document.querySelector('#hud'),
  hudInfo: document.querySelector('#hudInfo'),
  fitBtn: document.querySelector('#fitBtn'),
  console: document.querySelector('#console'),
  commands: document.querySelector('#commands'),
  log: document.querySelector('#log'),
  runBtn: document.querySelector('#runBtn'),
  saveBtn: document.querySelector('#saveBtn'),
  saveAsBtn: document.querySelector('#saveAsBtn'),
  downloadBtn: document.querySelector('#downloadBtn'),
  resetBtn: document.querySelector('#resetBtn'),
  closeBtn: document.querySelector('#closeBtn'),
  exampleBtn: document.querySelector('#exampleBtn'),
  statSize: document.querySelector('#statSize'),
  statBlocks: document.querySelector('#statBlocks'),
  statVersion: document.querySelector('#statVersion'),
  statStatus: document.querySelector('#statStatus'),
  busy: document.querySelector('#busy'),
  busyText: document.querySelector('#busyText'),
  dropHint: document.querySelector('#dropHint'),
  toasts: document.querySelector('#toasts'),
  modal: document.querySelector('#modal'),
};

export function setBusy(busy, text = '处理中…') {
  els.busy.classList.toggle('hidden', !busy);
  els.busyText.textContent = text;
  els.runBtn.disabled = busy;
}

export function setStatus(text, error = false) {
  els.statStatus.textContent = text;
  els.statStatus.style.color = error
    ? 'var(--err)'
    : text === '运行中'
      ? 'var(--accent)'
      : 'var(--ok)';
}

export function setLog(text, error = false) {
  els.log.textContent = text || '';
  els.log.classList.toggle('err', error);
  els.log.scrollTop = els.log.scrollHeight;
}

export function toast(message, type = 'ok') {
  const node = document.createElement('div');
  node.className = `toast ${type}`;
  node.textContent = message;
  els.toasts.append(node);
  setTimeout(() => {
    node.style.opacity = '0';
    setTimeout(() => node.remove(), 220);
  }, 3400);
}

export function setFileCount(count) {
  els.fileCount.textContent = String(count);
}

export function setHudInfo(text) {
  els.hudInfo.textContent = text;
}

export function setStats(state) {
  els.statSize.textContent = `${state.width} × ${state.height} × ${state.length}`;
  els.statBlocks.textContent = state.blockCount.toLocaleString();
  els.statVersion.textContent = state.dataVersion || '—';
}

export function showEmpty() {
  els.emptyState.classList.remove('hidden');
  els.hud.classList.add('hidden');
  els.console.classList.add('hidden');
  els.statSize.textContent = '—';
  els.statBlocks.textContent = '—';
  els.statVersion.textContent = '—';
  els.statStatus.textContent = '未载入';
  els.statStatus.style.color = 'var(--muted)';
  els.hudInfo.textContent = '拖动鼠标查看';
  els.log.textContent = '';
  document.title = 'WorldEdit 3D 模拟器';
}

export function showLoaded(state) {
  els.emptyState.classList.add('hidden');
  els.hud.classList.remove('hidden');
  els.console.classList.remove('hidden');
  setStats(state);
  setStatus('就绪');
  setHudInfo(`${state.name}${state.dirty ? ' · 未保存' : ''} · ${state.blockCount.toLocaleString()} 方块`);
  document.title = `${state.name} · WorldEdit 3D`;
}

export function setActions({ hasFile, dirty, busy }) {
  const disabled = !hasFile || busy;
  els.runBtn.disabled = disabled;
  els.resetBtn.disabled = disabled;
  els.saveAsBtn.disabled = disabled;
  els.downloadBtn.disabled = disabled;
  els.closeBtn.disabled = disabled;
  els.exampleBtn.disabled = disabled;
  els.saveBtn.disabled = disabled || !dirty;
}
