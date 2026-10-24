let menu = null;
let menuCleanup = null;

export function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export function formatDate(mtime) {
  const date = new Date(mtime * 1000);
  const now = new Date();
  const options = date.getFullYear() === now.getFullYear()
    ? { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }
    : { year: 'numeric', month: '2-digit', day: '2-digit' };
  return date.toLocaleString('zh-CN', options);
}

function closeMenu() {
  if (menu) {
    menu.remove();
    menu = null;
  }
  if (menuCleanup) {
    menuCleanup();
    menuCleanup = null;
  }
}

function openMenu(anchor, file, handlers) {
  closeMenu();
  const node = document.createElement('div');
  node.className = 'file-menu';
  const actions = [
    ['重命名', handlers.onRename],
    ['复制', handlers.onDuplicate],
    ['下载', handlers.onDownload],
    ['删除', handlers.onDelete, 'danger'],
  ];
  for (const [label, handler, tone] of actions) {
    if (!handler) continue;
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = label;
    if (tone) button.classList.add(tone);
    button.addEventListener('click', (event) => {
      event.stopPropagation();
      closeMenu();
      handler(file.name);
    });
    node.append(button);
  }
  document.body.append(node);
  const rect = anchor.getBoundingClientRect();
  node.style.left = `${Math.min(rect.right - node.offsetWidth, window.innerWidth - node.offsetWidth - 8)}px`;
  node.style.top = `${Math.min(rect.bottom + 4, window.innerHeight - node.offsetHeight - 8)}px`;

  const onDocument = (event) => {
    if (!node.contains(event.target)) closeMenu();
  };
  const onKey = (event) => {
    if (event.key === 'Escape') closeMenu();
  };
  setTimeout(() => document.addEventListener('pointerdown', onDocument), 0);
  document.addEventListener('keydown', onKey);
  window.addEventListener('resize', closeMenu, { once: true });
  menu = node;
  menuCleanup = () => {
    document.removeEventListener('pointerdown', onDocument);
    document.removeEventListener('keydown', onKey);
  };
}

export function renderFileList(container, files, options) {
  closeMenu();
  const {
    filter = '',
    sort = 'name',
    activeName = null,
    dirty = false,
    onLoad,
    onRename,
    onDuplicate,
    onDownload,
    onDelete,
  } = options;

  const query = filter.trim().toLowerCase();
  const items = files
    .filter((file) => file.name.toLowerCase().includes(query))
    .sort((a, b) => (sort === 'mtime' ? b.mtime - a.mtime : a.name.localeCompare(b.name, 'zh-CN')));

  container.textContent = '';
  if (!items.length) {
    const empty = document.createElement('li');
    empty.className = 'file-empty';
    empty.textContent = files.length ? '没有匹配的文件' : '暂无投影';
    container.append(empty);
    return;
  }

  for (const file of items) {
    const item = document.createElement('li');
    item.className = 'file-item';
    const active = file.name === activeName;
    if (active) item.classList.add('active');

    const main = document.createElement('button');
    main.type = 'button';
    main.className = 'file-main';
    const name = document.createElement('span');
    name.className = 'file-name';
    name.textContent = file.name;
    if (active && dirty) {
      const dot = document.createElement('span');
      dot.className = 'dirty-dot';
      dot.title = '有未保存修改';
      name.append(dot);
    }
    const meta = document.createElement('span');
    meta.className = 'file-meta';
    meta.textContent = `${formatSize(file.size)} · ${formatDate(file.mtime)}`;
    main.append(name, meta);
    main.addEventListener('click', () => onLoad(file.name));

    const more = document.createElement('button');
    more.type = 'button';
    more.className = 'file-menu-btn';
    more.textContent = '⋯';
    more.title = '更多操作';
    more.addEventListener('click', (event) => {
      event.stopPropagation();
      openMenu(more, file, { onRename, onDuplicate, onDownload, onDelete });
    });

    item.append(main, more);
    container.append(item);
  }
}
