import { Color } from 'three';

export const INVISIBLE = new Set([
  'minecraft:air',
  'minecraft:cave_air',
  'minecraft:void_air',
  'minecraft:structure_void',
  'minecraft:barrier',
  'minecraft:light',
]);

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

export const TRANSPARENT = new Set([
  'water', 'ice', 'frosted_ice', 'blue_ice', 'glass', 'glass_pane',
  'tinted_glass', 'slime_block', 'honey_block', 'bubble_column',
]);

for (const name of Object.keys(DYE)) {
  TRANSPARENT.add(`${name}_stained_glass`);
  TRANSPARENT.add(`${name}_stained_glass_pane`);
}

const cache = new Map();

function clamp(value, min = 0, max = 1) {
  return Math.min(max, Math.max(min, value));
}

function shade(hex, lightnessDelta, saturationScale) {
  const color = new Color(hex);
  const hsl = {};
  color.getHSL(hsl);
  color.setHSL(hsl.h, clamp(hsl.s * saturationScale), clamp(hsl.l + lightnessDelta));
  return `#${color.getHexString()}`;
}

function hashColor(text) {
  let hash = 2166136261;
  for (let index = 0; index < text.length; index += 1) {
    hash ^= text.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  const color = new Color();
  color.setHSL(((hash >>> 0) % 360) / 360, 0.4, 0.56);
  return `#${color.getHexString()}`;
}

export function baseName(stateName) {
  return stateName.split('[')[0].replace(/^minecraft:/, '');
}

export function colorFor(base) {
  if (cache.has(base)) return cache.get(base);
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
  cache.set(base, hex);
  return hex;
}
