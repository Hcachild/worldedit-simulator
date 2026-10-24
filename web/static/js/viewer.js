import * as THREE from 'three';
import { OrbitControls } from 'three/addons/OrbitControls.js';
import { INVISIBLE, TRANSPARENT, baseName, colorFor } from './colors.js';

function b64ToBytes(b64) {
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return bytes;
}

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

export class Viewer {
  constructor(canvas, container) {
    this.canvas = canvas;
    this.container = container;
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x111318);
    this.camera = new THREE.PerspectiveCamera(50, 1, 0.05, 4000);
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.controls = new OrbitControls(this.camera, canvas);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.08;
    this.controls.screenSpacePanning = true;
    this.controls.minDistance = 2;
    this.controls.maxDistance = 1500;
    this.controls.target.set(0, 1, 0);
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x2a2f3a, 1.5));
    const sun = new THREE.DirectionalLight(0xffffff, 1.7);
    sun.position.set(1, 2.2, 1.4);
    this.scene.add(sun);
    const fill = new THREE.DirectionalLight(0xffffff, 0.55);
    fill.position.set(-1.2, 1, -1.5);
    this.scene.add(fill);
    this.group = null;
    this.grid = null;
    this.pickables = [];
    this.current = null;
    this.blockTexture = null;
    this.pointerDown = null;
    this.raycaster = new THREE.Raycaster();
    this.pointer = new THREE.Vector2();
    this.onPick = null;
    this.updateGrid(0, 0);
    this.fitDefault();
    this.bindEvents();
    this.resize();
    new ResizeObserver(() => this.resize()).observe(container);
    window.addEventListener('resize', () => this.resize());
    this.renderer.setAnimationLoop(() => {
      this.controls.update();
      this.renderer.render(this.scene, this.camera);
    });
  }

  bindEvents() {
    this.canvas.addEventListener('pointerdown', (event) => {
      if (event.button === 0) this.pointerDown = { x: event.clientX, y: event.clientY };
    });
    this.canvas.addEventListener('pointerup', (event) => {
      if (!this.pointerDown) return;
      const moved = Math.hypot(event.clientX - this.pointerDown.x, event.clientY - this.pointerDown.y);
      this.pointerDown = null;
      if (moved <= 5) this.inspect(event);
    });
  }

  resize() {
    const width = this.container.clientWidth || 1;
    const height = this.container.clientHeight || 1;
    this.renderer.setSize(width, height, false);
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
  }

  getBlockTexture() {
    if (this.blockTexture) return this.blockTexture;
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
    this.blockTexture = new THREE.CanvasTexture(surface);
    this.blockTexture.magFilter = THREE.NearestFilter;
    this.blockTexture.minFilter = THREE.NearestFilter;
    this.blockTexture.colorSpace = THREE.SRGBColorSpace;
    return this.blockTexture;
  }

  disposeGroup(group) {
    group.traverse((child) => {
      if (child.geometry) child.geometry.dispose();
      if (child.material) {
        const materials = Array.isArray(child.material) ? child.material : [child.material];
        for (const material of materials) material.dispose();
      }
    });
  }

  addInstances(records, width, length, transparent) {
    if (!records.length) return;
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshLambertMaterial({
      color: 0xffffff,
      map: transparent ? null : this.getBlockTexture(),
      transparent,
      opacity: transparent ? 0.3 : 1,
      depthWrite: !transparent,
    });
    const mesh = new THREE.InstancedMesh(geometry, material, records.length);
    mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    const dummy = new THREE.Object3D();
    const color = new THREE.Color();
    for (let index = 0; index < records.length; index += 1) {
      const record = records[index];
      dummy.position.set(record.x - width / 2 + 0.5, record.y + 0.5, record.z - length / 2 + 0.5);
      dummy.updateMatrix();
      mesh.setMatrixAt(index, dummy.matrix);
      color.set(colorFor(record.base));
      mesh.setColorAt(index, color);
    }
    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    mesh.userData.blocks = records;
    this.group.add(mesh);
    this.pickables.push(mesh);
  }

  updateGrid(width, length) {
    if (this.grid) {
      this.scene.remove(this.grid);
      this.grid.geometry.dispose();
      this.grid.material.dispose();
    }
    if (!width || !length) {
      this.grid = new THREE.GridHelper(32, 32, 0x394152, 0x232833);
    } else {
      const span = Math.max(width, length, 8);
      const size = Math.ceil((span * 1.6) / 2) * 2;
      this.grid = new THREE.GridHelper(size, Math.min(size, 80), 0x394152, 0x232833);
    }
    this.grid.position.y = 0;
    this.scene.add(this.grid);
  }

  fitDefault() {
    this.controls.target.set(0, 1, 0);
    this.camera.position.set(26, 24, 32);
    this.camera.near = 0.1;
    this.camera.far = 1000;
    this.controls.maxDistance = 500;
    this.camera.updateProjectionMatrix();
    this.controls.update();
  }

  fitCamera(width, height, length) {
    const span = Math.max(width, height, length, 4);
    const distance = span * 1.9 + 6;
    this.controls.target.set(0, height / 2, 0);
    this.camera.position.set(distance * 0.85, height * 0.9 + span * 0.8, distance * 1.05);
    this.controls.maxDistance = Math.max(1500, distance * 6);
    this.camera.near = Math.max(0.05, distance / 2000);
    this.camera.far = distance * 30;
    this.camera.updateProjectionMatrix();
    this.controls.update();
  }

  clear() {
    if (this.group) {
      this.scene.remove(this.group);
      this.disposeGroup(this.group);
    }
    this.group = null;
    this.pickables = [];
    this.current = null;
    this.updateGrid(0, 0);
    this.fitDefault();
    if (this.onPick) this.onPick(null);
  }

  setModel(state, reframe = true) {
    if (!state) {
      this.clear();
      return;
    }
    if (this.group) {
      this.scene.remove(this.group);
      this.disposeGroup(this.group);
    }
    this.group = new THREE.Group();
    this.pickables = [];
    this.current = state;

    const { width, height, length, palette, data } = state;
    const indices = decodeVarints(b64ToBytes(data));
    const opaque = [];
    const transparent = [];
    for (let index = 0; index < indices.length; index += 1) {
      const name = palette[indices[index]];
      if (!name || INVISIBLE.has(name)) continue;
      const x = index % width;
      const z = Math.floor(index / width) % length;
      const y = Math.floor(index / (width * length));
      const base = baseName(name);
      const record = { x, y, z, name, base };
      if (TRANSPARENT.has(base)) transparent.push(record);
      else opaque.push(record);
    }

    this.addInstances(opaque, width, length, false);
    this.addInstances(transparent, width, length, true);
    this.scene.add(this.group);
    this.updateGrid(width, length);
    if (reframe) this.fitCamera(width, height, length);
  }

  fit() {
    if (this.current) {
      this.fitCamera(this.current.width, this.current.height, this.current.length);
    } else {
      this.fitDefault();
    }
  }

  inspect(event) {
    if (!this.pickables.length) {
      if (this.onPick) this.onPick(null);
      return;
    }
    const rect = this.canvas.getBoundingClientRect();
    this.pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    this.pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    this.raycaster.setFromCamera(this.pointer, this.camera);
    const hits = this.raycaster.intersectObjects(this.pickables, false);
    if (!hits.length) {
      if (this.onPick) this.onPick(null);
      return;
    }
    const hit = hits[0];
    const record = hit.object.userData.blocks[hit.instanceId];
    if (this.onPick) this.onPick(record || null);
  }
}
