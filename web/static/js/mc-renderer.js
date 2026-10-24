import * as THREE from 'three';
import { configure, createScene, prepareAssets } from '../vendor/block-model-renderer.min.js';

const ASSET_VERSION = '1.21.1';
const ASSET_JAR = '/assets/client.jar';

configure({ THREE, assetsUrl: '/assets.zip' });

export class AssetsMissingError extends Error {}

function decodeVarints(bytes) {
  const values = [];
  let value = 0;
  let shift = 0;
  for (let index = 0; index < bytes.length; index += 1) {
    const byte = bytes[index];
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

function b64ToBytes(b64) {
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return bytes;
}

export function parseState(stateName) {
  const bracket = stateName.indexOf('[');
  const id = bracket >= 0 ? stateName.slice(0, bracket) : stateName;
  const properties = {};
  if (bracket >= 0) {
    const end = stateName.lastIndexOf(']');
    const body = stateName.slice(bracket + 1, end > bracket ? end : undefined);
    for (const part of body.split(',')) {
      const equals = part.indexOf('=');
      if (equals > 0) properties[part.slice(0, equals)] = part.slice(equals + 1);
    }
  }
  return { id, properties };
}

const SKIP = new Set(['minecraft:air', 'minecraft:cave_air', 'minecraft:void_air']);

export function buildBlockData(state) {
  const { width, length, palette, data } = state;
  const indices = decodeVarints(b64ToBytes(data));
  const types = [];
  const raw = [];
  const records = [];
  const typeIndex = new Map();

  for (let index = 0; index < indices.length; index += 1) {
    const stateName = palette[indices[index]];
    if (!stateName || SKIP.has(stateName)) continue;
    const x = index % width;
    const z = Math.floor(index / width) % length;
    const y = Math.floor(index / (width * length));
    let type = typeIndex.get(stateName);
    if (type === undefined) {
      type = types.length;
      typeIndex.set(stateName, type);
      types.push(parseState(stateName));
    }
    raw.push(type, x, y, z);
    records.push({ x, y, z, name: stateName });
  }

  return {
    blocks: { palette: types, raw: Int32Array.from(raw) },
    records,
  };
}

export class MinecraftRenderer {
  constructor() {
    this.assets = null;
    this.loading = null;
  }

  async ensureAssets(onStatus) {
    if (this.assets) return this.assets;
    if (!this.loading) {
      this.loading = (async () => {
        if (onStatus) onStatus('下载材质包…');
        const response = await fetch(ASSET_JAR, { cache: 'force-cache' });
        if (!response.ok) throw new AssetsMissingError('缺少 Minecraft 材质包');
        const buffer = new Uint8Array(await response.arrayBuffer());
        if (onStatus) onStatus('解析材质包…');
        this.assets = await prepareAssets([buffer], { cache: true, version: ASSET_VERSION });
        return this.assets;
      })().catch((error) => {
        this.loading = null;
        throw error;
      });
    }
    return this.loading;
  }

  async build(state, { onProgress, shouldCancel, onStatus } = {}) {
    const { blocks, records } = buildBlockData(state);
    if (!blocks.raw.length) return { handle: null, records };
    const assets = await this.ensureAssets(onStatus);
    const handle = await createScene(assets, blocks, {
      version: ASSET_VERSION,
      lighting: { light: false, daytime: 'noon', brightness: 0.5 },
      optimize: true,
      animate: true,
      biome: { temperature: 0.8, downfall: 0.4 },
      onProgress,
      shouldCancel,
    });
    return { handle, records };
  }

  dispose(handle) {
    if (handle) handle.dispose();
  }
}

