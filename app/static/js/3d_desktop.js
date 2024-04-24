/*
Computer Desk by Zsky [CC-BY] (https://creativecommons.org/licenses/by/3.0/) via Poly Pizza (https://poly.pizza/m/OhXey2fljr)
*/

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import * as CANNON from 'cannon-es';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();

const world = new CANNON.World();
world.gravity.set(0, -9.81, 0);

camera.position.set(1, 1.5, 2);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(1, 1.5, 2);
directionalLight.castShadow = true;
scene.add(directionalLight);

const ambientLight = new THREE.AmbientLight(0x404040, 2.0);
scene.add(ambientLight);

const controls = new OrbitControls(camera, renderer.domElement);
controls.minDistance = 1.2;
controls.maxDistance = 3;
controls.maxPolarAngle = Math.PI / 1.9;
controls.enablePan = false;
controls.enableDamping = true;
controls.target.set(-0.235475134104492, 0.4, 0.0004267523835632392);

const cubeTextureLoader = new THREE.CubeTextureLoader();
const texture = cubeTextureLoader.load([
    '/skybox/px.png',
    '/skybox/nx.png',
    '/skybox/py.png',
    '/skybox/ny.png',
    '/skybox/pz.png',
    '/skybox/nz.png'
]);
scene.background = texture;

const gltfLoader = new GLTFLoader();
gltfLoader.load('/model/desk.glb', (gltf) => {
    gltf.scene.traverse((node) => {
        if (node.isMesh) {
            node.castShadow = true;
            node.receiveShadow = true;
        }
    });
    scene.add(gltf.scene);

    const deskBox = new THREE.Box3().setFromObject(gltf.scene);
    const center = deskBox.getCenter(new THREE.Vector3());
    const size = deskBox.getSize(new THREE.Vector3());

    const deskShape = new CANNON.Box(new CANNON.Vec3(size.x / 2, size.y / 2, size.z / 2));
    const deskBody = new CANNON.Body({ mass: 0 });
    deskBody.addShape(deskShape);
    deskBody.position.set(center.x, center.y, center.z);
    world.addBody(deskBody);
});

const textureLoader = new THREE.TextureLoader();
const groundTexture = textureLoader.load('/texture/concrete.png');
groundTexture.wrapS = THREE.RepeatWrapping;
groundTexture.wrapT = THREE.RepeatWrapping;
groundTexture.repeat.set(10, 10);

const groundGeometry = new THREE.CircleGeometry(5, 32);
const groundMaterial = new THREE.MeshStandardMaterial({ map: groundTexture });
const groundMesh = new THREE.Mesh(groundGeometry, groundMaterial);
groundMesh.rotation.x = -Math.PI / 2;
groundMesh.position.y = -0.3;
groundMesh.receiveShadow = true;
scene.add(groundMesh);

const groundShape = new CANNON.Plane();
const groundBody = new CANNON.Body({ mass: 0 });
groundBody.addShape(groundShape);
groundBody.position.y = -0.3;
world.addBody(groundBody);

function updatePhysics() {
    world.step(1 / 60);
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    updatePhysics();
    renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});