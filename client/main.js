import * as V from "@voxelize/core";
import * as T from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const enter = document.querySelector("#enter");
const phase = document.querySelector("#phase");
const party = document.querySelector("#party");
const spawn = [6 + Math.floor(Math.random() * 4), 6, 13];
const world = new V.World({ textureUnitDimension: 16 });
const renderer = new T.WebGLRenderer({ canvas: document.querySelector("canvas"), antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
const camera = new T.PerspectiveCamera(67, 1, 0.1, 300);
function resize() {
  renderer.setSize(innerWidth, innerHeight);
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
}
resize();
addEventListener("resize", resize);
const network = new V.Network();
const controls = new V.RigidControls(camera, renderer.domElement, world, { initialPosition: spawn });
const inputs = new V.Inputs();
inputs.setNamespace("game");
controls.connect(inputs, "game");
const peers = new V.Peers(controls.object);
peers.createPeer = () => new V.Character();
peers.onPeerUpdate = (peer, data) => {
  if (data.position && data.direction) peer.set(data.position, data.direction);
};
network.register(world, peers, controls);
world.add(peers);
world.add(new T.HemisphereLight(0xffdec8, 0xa7797a, 2.4));
const keyLight = new T.DirectionalLight(0xffc48c, 3);
keyLight.position.set(-12, 17, 9);
world.add(keyLight);

const origin = new T.Vector3();
const direction = new T.Vector3();
const floorMark = new T.Mesh(new T.PlaneGeometry(1, 1), new T.MeshBasicMaterial({
  color: 0xff953d, transparent: true, opacity: .38, depthWrite: false, side: T.DoubleSide,
}));
floorMark.rotation.x = -Math.PI / 2;
floorMark.position.set(0, 4.02, 0);
floorMark.scale.set(5, 29, 1);
world.add(floorMark);
const flame = new T.Mesh(new T.ConeGeometry(2.75, 27, 8, 1, true), new T.MeshBasicMaterial({
  color: 0xff9d38, side: T.DoubleSide, transparent: true, opacity: .74, depthWrite: false,
}));
const mouth = new T.Vector3();
const breathEnd = new T.Vector3(0, 4.25, 14);
const breathAxis = new T.Vector3();
const up = new T.Vector3(0, 1, 0);
world.add(flame);

let dragon, head, jaw, leftWing, rightWing;
function animate() {
  requestAnimationFrame(animate);
  if (!dragon || !world.isInitialized) return;
  const t = world.time % 12;
  const warning = t >= 6 && t < 9;
  const fire = t >= 9 && t < 10.6;
  const inhale = T.MathUtils.smoothstep(t, 6, 8.85) * (1 - T.MathUtils.smoothstep(t, 8.85, 9.25));
  const exhale = T.MathUtils.smoothstep(t, 8.85, 9.2) * (1 - T.MathUtils.smoothstep(t, 10.45, 11.1));
  head.rotation.x = .025 * Math.sin(t * 1.8) - .19 * inhale + .15 * exhale;
  head.rotation.y = .06 * Math.sin(t * Math.PI / 6) * (1 - exhale);
  jaw.rotation.x = .055 + .09 * inhale + .32 * exhale;
  leftWing.rotation.z = .036 * Math.sin(t * Math.PI / 3) + .14 * inhale;
  rightWing.rotation.z = -leftWing.rotation.z;
  floorMark.visible = warning || fire;
  floorMark.material.opacity = fire ? .72 : .27 + .18 * Math.sin(t*9);
  flame.visible = fire;
  if (fire) {
    // The head pivot is at the base of the neck; the muzzle moves with it.
    head.localToWorld(mouth.set(.4813, .7166, 4.3873));
    breathAxis.subVectors(mouth, breathEnd);
    flame.position.lerpVectors(mouth, breathEnd, .5);
    flame.scale.set(1 + .07 * Math.sin(t * 30), breathAxis.length() / 27, 1);
    flame.quaternion.setFromUnitVectors(up, breathAxis.normalize());
  }
  const label = !network.connected ? "连接已断开" : fire ? "吐息" : warning ? "吸气 · 避开亮带" : "待机";
  if (phase.textContent !== label) phase.textContent = label;
  camera.getWorldDirection(direction);
  world.update(controls.object.getWorldPosition(origin), direction);
  controls.update();
  if (origin.y < -3) controls.teleport(...spawn);
  peers.update();
  for (const peer of peers.map.values()) {
    peer.visible = peer.position.distanceTo(controls.object.position) > 1.1;
  }
  party.textContent = network.connected ? (peers.map.size + 1) + " 人在场" : "离线";
  renderer.render(world, camera);
}
const canvas = renderer.domElement;
const help = document.querySelector("footer span");
const defaultHelp = help.textContent;
let dragMode = false;
function leaveDragMode() {
  if (!dragMode) return;
  dragMode = false;
  controls.isLocked = false;
  controls.resetMovements();
  enter.hidden = false;
  help.textContent = defaultHelp;
}
async function enterWorld(event) {
  event.stopImmediatePropagation();
  if (dragMode || document.pointerLockElement || enter.disabled) return;
  try {
    await canvas.requestPointerLock();
  } catch {
    // Some embedded browsers only provide ordinary pointer movement.
    dragMode = true;
    controls.isLocked = true;
    enter.hidden = true;
    help.textContent = "WASD 移动　·　按住鼠标拖动环视　·　空格跳跃　·　Esc 暂停";
  }
}
enter.addEventListener("click", enterWorld);
canvas.addEventListener("click", enterWorld, true);
canvas.addEventListener("mousemove", event => {
  if (dragMode && !(event.buttons & 1)) event.stopImmediatePropagation();
}, true);
document.addEventListener("pointerlockchange", () => { enter.hidden = !!document.pointerLockElement || dragMode; });
addEventListener("keydown", event => { if (event.key === "Escape") leaveDragMode(); });
addEventListener("blur", leaveDragMode);

async function start() {
  await network.connect(import.meta.env.VITE_WOB_SERVER || "http://127.0.0.1:4100");
  await network.join("ember-vault");
  await world.initialize();
  world.renderRadius = 4;
  world.chunkRenderer.uniforms.baseAmbient.value = .65;
  await Promise.all(["Basalt", "Slate", "Cinder", "Ember"].map(async block => {
    const tile = new Image();
    tile.src = "/stone/" + block.toLowerCase() + ".png";
    await tile.decode();
    world.applyBlockTexture(block, ["px","nx","py","ny","pz","nz"], tile);
  }));
  const model = await new GLTFLoader().loadAsync("/models/cinderwing.gltf");
  dragon = model.scene;
  head = dragon.getObjectByName("Head");
  jaw = dragon.getObjectByName("Jaw");
  leftWing = dragon.getObjectByName("LeftWing");
  rightWing = dragon.getObjectByName("RightWing");
  dragon.position.set(0, 5, -22.5);
  world.add(dragon);
  controls.setDirection(-spawn[0], 3, -33);
  enter.disabled = false;
  animate();
}
start().catch(error => {
  console.error(error);
  party.textContent = "未就绪";
  phase.textContent = "加载失败，请检查本地服务后刷新";
});
