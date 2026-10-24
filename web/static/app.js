import * as THREE from 'three';
import { OrbitControls } from 'three/addons/OrbitControls.js';

const canvas = document.querySelector('#view');
const main = document.querySelector('#main');
const els = {
  fileList: document.querySelector('#fileList'),
  fileInput: document.querySelector('#fileInput'),
  uploadBtn: document.querySelector('#uploadBtn'),
  statSize: document.querySelector('#statSize'),
  statBlocks: document.querySelector('#statBlocks'),
  statVersion: document.querySelector('#statVersion'),
  statStatus: document.querySelector('#statStatus'),
  hudInfo: document.querySelector('#hudInfo'),
  commands: document.querySelector('#commands'),
  log: document.querySelector('#log'),
  runBtn: document.querySelector('#runBtn'),
  resetBtn: document.querySelector('#resetBtn'),
  downloadBtn: document.querySelector('#downloadBtn'),
  saveBtn: document.querySelector('#saveBtn'),
  exampleBtn: document.querySelector('#exampleBtn'),
  fitBtn: document.querySelector('#fitBtn'),
  busy: document.querySelector('#busy'),
  busyText: document.querySelector('#busyText'),
  dropHint: document.querySelector('#dropHint'),
};

let scene;
let camera;
let renderer;
let controls;
let worldGroup = null;
let gridHelper = null;
let pickables = [];
let currentState = null;
let pointerDown = null;
let blockTexture = null;
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

const DYE = {
  white: '#e9ecef', orange: '#f08a24', magenta: '#c74ebf', light_blue: '#58b7d8',
  yellow: '#f3d03e', lime: '#7fcc4a', pink: '#f0a0b8', gray: '#4a4f55',
  light_gray: '#a8adb2', cyan: '#2f8f9d', purple: '#7a3fb0', blue: '#3546a8',
  brown: '#6f4b2e', green: '#3f6b2e', red: '#a83232', black: '#1e1f22',
};

const WOOD = {
  oak: '#b58b5a', spruce: '#7a5230', birch: '#d7c185', jungle: '#a87a4f',
  acacia: '#b5623c', dark_oak: '#5b3d22', mangrove: '#7a4b3a', cherry: '#e6b7b0',
  bamboo: '#c8a75b', crimson: '#7c3b52', warped: '#3a6b66',
};

const COLORS = {
  stone: '#8b8f94', cobblestone: '#7b7f83', mossy_cobblestone: '#6f7d63',
  granite: '#9a6b5b', diorite: '#cfcfca', andesite: '#8d8d8a', deepslate: '#4b4d52',
  tuff: '#6b6a5e', calcite: '#dcdcd5', dripstone_block: '#8b5a44',
  dirt: '#8b5a2b', coarse_dirt: '#7a4e26', rooted_dirt: '#7d5a3c',
  grass_block: '#6aa84f', podzol: '#6b4f2a', mycelium: '#8a7b8c', farmland: '#6b4a2a',
  mud: '#4b3b32', clay: '#a4a8b8', gravel: '#9a9a9a', sand: '#e0d6a8',
  red_sand: '#c47a3a', sandstone: '#dbd0a3', red_sandstone: '#c47a3a',
  oak_planks: WOOD.oak, spruce_planks: WOOD.spruce, birch_planks: WOOD.birch,
  jungle_planks: WOOD.jungle, acacia_planks: WOOD.acacia, dark_oak_planks: WOOD.dark_oak,
  mangrove_planks: WOOD.mangrove, cherry_planks: WOOD.cherry, bamboo_planks: WOOD.bamboo,
  crimson_planks: WOOD.crimson, warped_planks: WOOD.warped,
  oak_log: '#6b4f2a', spruce_log: '#4a3420', birch_log: '#d7d3c3', jungle_log: '#5b432a',
  acacia_log: '#6b4a33', dark_oak_log: '#3d2b18', cherry_log: '#8a5a55', mangrove_log: '#5a3a2a',
  oak_leaves: '#4f7f3a', spruce_leaves: '#3b5f33', birch_leaves: '#6f9a4a',
  jungle_leaves: '#3f7f33', acacia_leaves: '#6b8f3a', dark_oak_leaves: '#33552a',
  cherry_leaves: '#e6a8b8', mangrove_leaves: '#4f7f3a', azalea_leaves: '#5f8f4a',
  flowering_azalea_leaves: '#b06fa0',
  water: '#3b6fd4', lava: '#e25822', ice: '#a8d8f0', snow_block: '#f2f2f2',
  snow: '#f2f2f2', powder_snow: '#f5f7fa', glass: '#cfe8ff', glass_pane: '#cfe8ff',
  tinted_glass: '#3a3f48', bedrock: '#55565a', obsidian: '#241a33',
  crying_obsidian: '#3a1f5c', netherrack: '#6e2b2b', soul_sand: '#5a4436',
  soul_soil: '#4b382b', basalt: '#4a4a50', blackstone: '#2f2b30', end_stone: '#dcdca8',
  purpur_block: '#a97aa9', glowstone: '#f5d76e', sea_lantern: '#cfe8e0',
  shroomlight: '#f0a04a', lantern: '#f5c46e', torch: '#f5c46e', brick: '#a44a3f',
  stone_bricks: '#8f8f8f', mossy_stone_bricks: '#6f7d63', cracked_stone_bricks: '#7f7f7f',
  chiseled_stone_bricks: '#8a8a8a', nether_bricks: '#3a1a1a', red_nether_bricks: '#5a1f1f',
  quartz_block: '#ece9e2', smooth_quartz: '#ece9e2', prismarine: '#63a89a',
  dark_prismarine: '#2f5a4f', gold_block: '#f2c94c', iron_block: '#d8d8d8',
  diamond_block: '#4fd1c5', emerald_block: '#2ecc71', lapis_block: '#2a4fa8',
  redstone_block: '#b02020', coal_block: '#1b1b1b', copper_block: '#c06a3e',
  oxidized_copper: '#4f9a86', amethyst_block: '#8f6fc0', hay_block: '#c8a13a',
  bookshelf: '#8a6a43', crafting_table: '#9a6a3a', furnace: '#6b6b6b',
  chest: '#9a6a3a', barrel: '#8a6238', melon: '#7aa83a', pumpkin: '#d68a2a',
  cactus: '#4f7f3a', bamboo: '#7aa83a', sugar_cane: '#8fbf6a', vine: '#4f7f3a',
  moss_block: '#5f7f3a', sculk: '#1f2b33', spawner: '#2a3038',
};

const INVISIBLE = new Set(['minecraft:air', 'minecraft:cave_air', 'minecraft:void_air', 'minecraft:structure_void', 'minecraft:barrier', 'minecraft:light']);
const TRANSPARENT = new Set(['water', 'ice', 'frosted_ice', 'blue_ice', 'glass', 'glass_pane', 'tinted_glass', 'slime_block', 'honey_block', 'bubble_column']);
for (const name of Object.keys(DYE)) {
  TRANSPARENT.add(`${name}_stained_glass`);
  TRANSPARENT.add(`${name}_stained_glass_pane`);
}

const colorCache = new Map();

function clamp(value, min = 0, max = 1) {
  return Math.min(max, Math.max(min, value));
}

function shade(hex, lightnessDelta, saturationScale) {
  const color = new THREE.Color(hex);
  const hsl = {};
  color.getHSL(hsl);
  color.setHSL(hsl.h, clamp(hsl.s * saturationScale), clamp(hsl.l + lightnessDelta));
  return `#${color.getHexString()}`;
}

function hashColor(text) {
  let hash = 2166136261;
  for (let i = 0; i < text.length; i += 1) {
    hash ^= text.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  const color = new THREE.Color();
  color.setHSL(((hash >>> 0) % 360) / 360, 0.4, 0.56);
  return `#${color.getHexString()}`;
}

function colorFor(base) {
  if (colorCache.has(base)) return colorCache.get(base);
  let hex = COLORS[base];
  if (!hex) {
    const dyed = base.match(/^(light_blue|light_gray|white|orange|magenta|yellow|lime|pink|gray|cyan|purple|blue|brown|green|red|black)_(wool|carpet|concrete|concrete_powder|terracotta|stained_glass|stained_glass_pane|bed)$/);
    if (dyed) {
      hex = DYE[dyed[1]];
      if (dyed[2] === 'terracotta') hex = shade(hex, -0.2, 0.72);
      if (dyed[2] === 'concrete_powder') hex = shade(hex, -0.05, 0.8);
      if (dyed[2] === 'carpet') hex = shade(hex, -0.02, 0.95);
    }
  }
  if (!hex) {
    const wood = base.match(/^(oak|spruce|birch|jungle|acacia|dark_oak|mangrove|cherry|bamboo|crimson|warped)_(planks|log|wood|leaves)$/);
    if (wood) {
      hex = WOOD[wood[1]];
      if (wood[2] === 'log' || wood[2] === 'wood') hex = shade(hex, -0.13, 0.9);
      if (wood[2] === 'leaves') hex = shade(hex, 0.02, 1.1);
    }
  }
  if (!hex) hex = hashColor(base);
  colorCache.set(base, hex);
  return hex;
}

function baseName(stateName) {
  return stateName.split('[')[0].replace(/^minecraft:/, '');
}

function getBlockTexture() {
  if (blockTexture) return blockTexture;
  const size = 16;
  const surface = document.createElement('canvas');
  surface.width = size;
  surface.height = size;
  const context = surface.getContext('2d');
  const image = context.createImageData(size, size);
  for (let y = 0; y < size; y += 1) {
    for (let x = 0; x < size; x += 1) {
      const edge = x === 0 || y === 0 || x === size - 1 || y === size - 1;
      const noise = ((x * 7 + y * 13 + ((x * y) % 5)) % 7) - 3;
      let value = 236 + noise * 4;
      if (edge) value = 206 + noise * 3;
      const index = (y * size + x) * 4;
      image.data[index] = value;
      image.data[index + 1] = value;
      image.data[index + 2] = value;
      image.data[index + 3] = 255;
    }
  }
  context.putImageData(image, 0, 0);
  blockTexture = new THREE.CanvasTexture(surface);
  blockTexture.magFilter = THREE.NearestFilter;
  blockTexture.minFilter = THREE.NearestFilter;
  blockTexture.colorSpace = THREE.SRGBColorSpace;
  return blockTexture;
}

function b64ToBytes(b64) {
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
  return bytes;
}

function decodeVarints(bytes) {
  const values = [];
  let value = 0;
  let shift = 0;
  for (let i = 0; i < bytes.length; i += 1) {
    const byte = bytes[i];
    value |= (byte & 0x7f) << shift;
    if (byte & 0x80) {
      shift += 7;
    } else {
      values.push(value >>> 0);
      value = 0;
      shift = 0;
    }
  }
  return values;
}

function initScene() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x111318);

  camera = new THREE.PerspectiveCamera(50, 1, 0.05, 4000);
  camera.position.set(24, 20, 30);

  renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.screenSpacePanning = true;
  controls.minDistance = 2;
  controls.maxDistance = 1500;

  scene.add(new THREE.HemisphereLight(0xffffff, 0x2a2f3a, 1.5));
  const sun = new THREE.DirectionalLight(0xffffff, 1.7);
  sun.position.set(1, 2.2, 1.4);
  scene.add(sun);
  const fill = new THREE.DirectionalLight(0xffffff, 0.55);
  fill.position.set(-1.2, 1, -1.5);
  scene.add(fill);

  resize();
  new ResizeObserver(resize).observe(main);
  window.addEventListener('resize', resize);

  canvas.addEventListener('pointerdown', (event) => {
    if (event.button === 0) pointerDown = { x: event.clientX, y: event.clientY };
  });
  canvas.addEventListener('pointerup', (event) => {
    if (!pointerDown) return;
    const moved = Math.hypot(event.clientX - pointerDown.x, event.clientY - pointerDown.y);
    pointerDown = null;
    if (moved > 5) return;
    inspect(event);
  });

  renderer.setAnimationLoop(() => {
    controls.update();
    renderer.render(scene, camera);
  });
}

function resize() {
  const width = main.clientWidth || 1;
  const height = main.clientHeight || 1;
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}

function disposeObject(object) {
  object.traverse((child) => {
    if (child.geometry) child.geometry.dispose();
    if (child.material) {
      const materials = Array.isArray(child.material) ? child.material : [child.material];
      for (const material of materials) material.dispose();
    }
  });
}

function updateGrid(width, height, length) {
  if (gridHelper) {
    scene.remove(gridHelper);
    gridHelper.geometry.dispose();
    gridHelper.material.dispose();
  }
  const span = Math.max(width, length, 8);
  const size = Math.ceil((span * 1.6) / 2) * 2;
  gridHelper = new THREE.GridHelper(size, Math.min(size, 80), 0x394152, 0x232833);
  gridHelper.position.y = 0;
  scene.add(gridHelper);
}

function fitCamera(width, height, length) {
  const span = Math.max(width, height, length, 4);
  const distance = span * 1.9 + 6;
  controls.target.set(0, height / 2, 0);
  camera.position.set(distance * 0.85, height * 0.9 + span * 0.8, distance * 1.05);
  controls.maxDistance = Math.max(1500, distance * 6);
  camera.near = Math.max(0.05, distance / 2000);
  camera.far = distance * 30;
  camera.updateProjectionMatrix();
  controls.update();
}

function addInstances(records, width, length, transparent) {
  if (!records.length) return;
  const geometry = new THREE.BoxGeometry(1, 1, 1);
  const material = new THREE.MeshLambertMaterial({
    color: 0xffffff,
    map: transparent ? null : getBlockTexture(),
    transparent,
    opacity: transparent ? 0.3 : 1,
    depthWrite: !transparent,
  });
  const mesh = new THREE.InstancedMesh(geometry, material, records.length);
  mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  const dummy = new THREE.Object3D();
  const color = new THREE.Color();

  for (let i = 0; i < records.length; i += 1) {
    const record = records[i];
    dummy.position.set(record.x - width / 2 + 0.5, record.y + 0.5, record.z - length / 2 + 0.5);
    dummy.updateMatrix();
    mesh.setMatrixAt(i, dummy.matrix);
    color.set(colorFor(record.base));
    mesh.setColorAt(i, color);
  }
  mesh.instanceMatrix.needsUpdate = true;
  if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
  mesh.userData.blocks = records;
  mesh.userData.transparent = transparent;
  worldGroup.add(mesh);
  pickables.push(mesh);
}

function buildModel(state, reframe) {
  currentState = state;
  if (worldGroup) {
    scene.remove(worldGroup);
    disposeObject(worldGroup);
  }
  worldGroup = new THREE.Group();
  pickables = [];

  const { width, height, length, palette, data } = state;
  const indices = decodeVarints(b64ToBytes(data));
  const opaque = [];
  const transparent = [];

  for (let i = 0; i < indices.length; i += 1) {
    const name = palette[indices[i]];
    if (!name || INVISIBLE.has(name)) continue;
    const x = i % width;
    const z = Math.floor(i / width) % length;
    const y = Math.floor(i / (width * length));
    const base = baseName(name);
    const record = { x, y, z, name, base };
    if (TRANSPARENT.has(base)) transparent.push(record);
    else opaque.push(record);
  }

  addInstances(opaque, width, length, false);
  addInstances(transparent, width, length, true);
  scene.add(worldGroup);
  updateGrid(width, height, length);
  if (reframe) fitCamera(width, height, length);

  els.statSize.textContent = `${width} × ${height} × ${length}`;
  els.statBlocks.textContent = state.blockCount.toLocaleString();
  els.statVersion.textContent = state.dataVersion || '-';
  els.hudInfo.textContent = `${state.name} · ${state.blockCount.toLocaleString()} 方块`;
  document.title = `${state.name} · WorldEdit 3D`;
}

function inspect(event) {
  const rect = canvas.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const hits = raycaster.intersectObjects(pickables, false);
  if (!hits.length) {
    els.hudInfo.textContent = '未选中方块';
    return;
  }
  const hit = hits[0];
  const record = hit.object.userData.blocks[hit.instanceId];
  if (record) {
    els.hudInfo.textContent = `${record.name} @ (${record.x}, ${record.y}, ${record.z})`;
  }
}

function setBusy(busy, text = '处理中…') {
  els.busy.classList.toggle('hidden', !busy);
  els.busyText.textContent = text;
  els.runBtn.disabled = busy;
}

function setStatus(text, error = false) {
  els.statStatus.textContent = text;
  els.statStatus.style.color = error ? 'var(--err)' : 'var(--ok)';
}

function setLog(text, error = false) {
  els.log.textContent = text || '';
  els.log.classList.toggle('err', error);
  els.log.scrollTop = els.log.scrollHeight;
}

async function api(path, options) {
  const response = await fetch(path, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok || data.ok === false) {
    throw new Error(data.error || `HTTP ${response.status}`);
  }
  return data;
}

async function refreshFiles() {
  try {
    const data = await api('/api/files');
    els.fileList.textContent = '';
    for (const file of data.files) {
      const item = document.createElement('li');
      const button = document.createElement('button');
      button.type = 'button';
      if (file.active) button.classList.add('active');
      const label = document.createElement('span');
      label.textContent = file.name;
      const size = document.createElement('span');
      size.className = 'size';
      size.textContent = file.size > 1024 * 1024
        ? `${(file.size / 1024 / 1024).toFixed(1)} MB`
        : `${Math.max(1, Math.round(file.size / 1024))} KB`;
      button.append(label, size);
      button.addEventListener('click', () => loadFile(file.name));
      item.append(button);
      els.fileList.append(item);
    }
  } catch (error) {
    setLog(`读取文件列表失败：${error.message}`, true);
  }
}

async function loadFile(name) {
  setBusy(true, '载入投影…');
  try {
    const data = await api('/api/load', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    });
    buildModel(data.state, true);
    setStatus('就绪');
    setLog(`已载入 ${name}`);
    await refreshFiles();
  } catch (error) {
    setStatus('错误', true);
    setLog(`载入失败：${error.message}`, true);
  } finally {
    setBusy(false);
  }
}

async function runCommands() {
  const text = els.commands.value.trim();
  if (!text) {
    setLog('请输入 WorldEdit 命令', true);
    return;
  }
  setBusy(true, 'WorldEdit 正在执行…');
  setStatus('运行中');
  try {
    const response = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ commands: text }),
    });
    const data = await response.json();
    if (data.log) setLog(data.log);
    if (data.state) buildModel(data.state, false);
    if (!response.ok || data.ok === false) {
      setStatus('错误', true);
      if (data.error) setLog(`${data.log ? `${data.log}\n\n` : ''}${data.error}`, true);
    } else {
      setStatus('就绪');
      if (!data.log) setLog('执行完成');
    }
  } catch (error) {
    setStatus('错误', true);
    setLog(`执行失败：${error.message}`, true);
  } finally {
    setBusy(false);
  }
}

async function resetFile() {
  setBusy(true, '重置中…');
  try {
    const data = await api('/api/reset', { method: 'POST' });
    buildModel(data.state, true);
    setStatus('就绪');
    setLog('已恢复到原始投影');
  } catch (error) {
    setStatus('错误', true);
    setLog(`重置失败：${error.message}`, true);
  } finally {
    setBusy(false);
  }
}

async function saveAs() {
  if (!currentState) return;
  const suggested = currentState.name || 'result.schem';
  const name = window.prompt('另存为（保存到 schematics/）', suggested.replace(/\.schem$/i, '_out.schem'));
  if (!name) return;
  try {
    const data = await api('/api/save-as', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    });
    setLog(`已保存 schematics/${data.name}`);
    await refreshFiles();
  } catch (error) {
    setLog(`保存失败：${error.message}`, true);
  }
}

async function uploadFile(file) {
  if (!file) return;
  setBusy(true, `上传 ${file.name}…`);
  try {
    const buffer = await file.arrayBuffer();
    const data = await api(`/api/upload?name=${encodeURIComponent(file.name)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/octet-stream' },
      body: buffer,
    });
    buildModel(data.state, true);
    setStatus('就绪');
    setLog(`已载入 ${data.state.name}`);
    await refreshFiles();
  } catch (error) {
    setStatus('错误', true);
    setLog(`上传失败：${error.message}`, true);
  } finally {
    setBusy(false);
  }
}

function fillExample() {
  if (!currentState) return;
  const { width, height, length } = currentState;
  els.commands.value = [
    '//pos1 0,0,0',
    `//pos2 ${width - 1},${height - 1},${length - 1}`,
    '//replace minecraft:oak_planks minecraft:birch_planks',
    '//replace minecraft:spruce_planks minecraft:gold_block',
    '//replace minecraft:glass minecraft:light_blue_stained_glass',
  ].join('\n');
}

const history = [];
let historyIndex = -1;

function setupEvents() {
  els.runBtn.addEventListener('click', runCommands);
  els.resetBtn.addEventListener('click', resetFile);
  els.downloadBtn.addEventListener('click', () => {
    if (currentState) window.location.href = '/api/download';
  });
  els.saveBtn.addEventListener('click', saveAs);
  els.exampleBtn.addEventListener('click', fillExample);
  els.fitBtn.addEventListener('click', () => {
    if (currentState) fitCamera(currentState.width, currentState.height, currentState.length);
  });

  els.uploadBtn.addEventListener('click', () => els.fileInput.click());
  els.fileInput.addEventListener('change', () => {
    uploadFile(els.fileInput.files[0]);
    els.fileInput.value = '';
  });

  els.commands.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      runCommands();
      return;
    }
    if (event.key === 'ArrowUp' && els.commands.value.trim() === '' && history.length) {
      event.preventDefault();
      historyIndex = Math.max(0, historyIndex < 0 ? history.length - 1 : historyIndex - 1);
      els.commands.value = history[historyIndex];
    } else if (event.key === 'ArrowDown' && historyIndex >= 0) {
      event.preventDefault();
      historyIndex += 1;
      if (historyIndex >= history.length) {
        historyIndex = -1;
        els.commands.value = '';
      } else {
        els.commands.value = history[historyIndex];
      }
    }
  });

  els.commands.addEventListener('change', () => {
    const value = els.commands.value.trim();
    if (value && history[history.length - 1] !== value) {
      history.push(value);
      if (history.length > 50) history.shift();
      historyIndex = -1;
    }
  });

  let dragDepth = 0;
  main.addEventListener('dragenter', (event) => {
    event.preventDefault();
    dragDepth += 1;
    els.dropHint.classList.remove('hidden');
  });
  main.addEventListener('dragover', (event) => event.preventDefault());
  main.addEventListener('dragleave', () => {
    dragDepth = Math.max(0, dragDepth - 1);
    if (dragDepth === 0) els.dropHint.classList.add('hidden');
  });
  main.addEventListener('drop', (event) => {
    event.preventDefault();
    dragDepth = 0;
    els.dropHint.classList.add('hidden');
    const file = event.dataTransfer.files[0];
    if (file) uploadFile(file);
  });
}

async function start() {
  initScene();
  setupEvents();
  await refreshFiles();
  try {
    const data = await api('/api/state');
    buildModel(data, true);
    setStatus('就绪');
    setLog('已就绪。输入命令后按 Ctrl+Enter 运行。');
  } catch (error) {
    setStatus('未载入', true);
    setLog('还没有载入投影：点击左侧文件，或把 .schem 拖进窗口。');
  }
}

start();
