import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js';

const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a0d14);

const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(12, 18, 16);
camera.lookAt(0, 0, 0);

const light = new THREE.DirectionalLight(0xffffff, 1.2);
light.position.set(15, 25, 10);
scene.add(light);
scene.add(new THREE.AmbientLight(0x8888aa, 0.6));

const terrainColor = { plains: 0x5ba85b, forest: 0x2e6b3a, hills: 0x8a7d52, mountains: 0x888888, desert: 0xd3c27a };
let tiles = [];
let currentSession = null;

function resize() {
  renderer.setSize(window.innerWidth, window.innerHeight);
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
}
window.addEventListener('resize', resize);
resize();

function clearTiles() {
  for (const t of tiles) scene.remove(t);
  tiles = [];
}

function renderState(state) {
  clearTiles();
  const { width, height, provinces, player, world_inflation, turn } = state;
  provinces.forEach((p) => {
    const x = (p.id % width) - width / 2;
    const z = Math.floor(p.id / width) - height / 2;
    const h = 0.4 + p.infrastructure * 0.18 + (p.stability / 100) * 0.5;
    const geo = new THREE.BoxGeometry(0.95, h, 0.95);
    const ownedByPlayer = p.owner === player.name;
    const mat = new THREE.MeshStandardMaterial({ color: ownedByPlayer ? 0x33ccff : terrainColor[p.terrain] ?? 0x777777 });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(x, h / 2, z);
    scene.add(mesh);
    tiles.push(mesh);
  });

  document.getElementById('stats').textContent =
`Empire: ${player.name}
Turn: ${turn}
Treasury: ${player.treasury.toFixed(1)}
Empire Inflation: ${(player.inflation*100).toFixed(2)}%
World Inflation: ${(world_inflation*100).toFixed(2)}%
Provinces: ${player.provinces}`;
}

async function api(path, method = 'GET', payload = null) {
  const res = await fetch(path, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: payload ? JSON.stringify(payload) : null,
  });
  return res.json();
}

document.getElementById('newGame').onclick = async () => {
  const empire_name = document.getElementById('empireName').value;
  const difficulty = document.getElementById('difficulty').value;
  const data = await api('/api/new-game', 'POST', { empire_name, difficulty });
  currentSession = data.session;
  renderState(data.state);
};

document.getElementById('nextTurn').onclick = async () => {
  if (!currentSession) return;
  const data = await api('/api/next-turn', 'POST', { session: currentSession });
  renderState(data.state);
};

function animate() {
  requestAnimationFrame(animate);
  tiles.forEach((t) => (t.rotation.y += 0.0015));
  renderer.render(scene, camera);
}
animate();
