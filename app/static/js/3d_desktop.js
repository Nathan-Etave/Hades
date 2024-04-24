/*
Computer Desk by Zsky [CC-BY] (https://creativecommons.org/licenses/by/3.0/) via Poly Pizza (https://poly.pizza/m/OhXey2fljr)
Laptop by Poly by Google [CC-BY] (https://creativecommons.org/licenses/by/3.0/) via Poly Pizza (https://poly.pizza/m/csEfSvMgyOw)
Debris Papers by Quaternius (https://poly.pizza/m/MujITy1NRR)
*/

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import * as CANNON from 'cannon-es';
import { TWEEN } from 'https://unpkg.com/three@0.139.0/examples/jsm/libs/tween.module.min.js';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();

const world = new CANNON.World();
world.gravity.set(0, -9.81, 0);

camera.position.set(1, 1.5, 2);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

const directionalLight = new THREE.DirectionalLight(0xffffff, 5);
directionalLight.position.set(1, 1.5, 2);
directionalLight.castShadow = true;
scene.add(directionalLight);

const ambientLight = new THREE.AmbientLight(0x404040, 10.0);
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
            node.name = 'desk';
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

    const topDesk = new THREE.Mesh(new THREE.BoxGeometry(size.x, 0, size.z), new THREE.MeshStandardMaterial({ transparent: true, opacity: 0.0 }));
    topDesk.position.set(center.x, center.y + size.y / 2, center.z);
    topDesk.name = 'topDesk';
    scene.add(topDesk);

    const borderDesk = new THREE.Mesh(new THREE.BoxGeometry(size.x, size.y, size.z), new THREE.MeshStandardMaterial({ transparent: true, opacity: 0.0 }));
    borderDesk.position.set(center.x, center.y - 0.001, center.z);
    borderDesk.name = 'borderDesk';
    scene.add(borderDesk);
});

gltfLoader.load('/model/laptop.glb', (gltf) => {
    gltf.scene.traverse((node) => {
        if (node.isMesh) {
            node.name = 'laptop';
            node.castShadow = true;
            node.receiveShadow = true;
        }
    });
    gltf.scene.scale.set(0.003, 0.003, 0.003);
    gltf.scene.rotation.x = -Math.PI / 2;
    gltf.scene.rotation.z = -Math.PI / 3;
    gltf.scene.position.set(-0.85, 0.39, -0.15);
    scene.add(gltf.scene);
});

gltfLoader.load('/model/debris.glb', (gltf) => {
    gltf.scene.traverse((node) => {
        if (node.isMesh) {
            node.castShadow = true;
            node.receiveShadow = true;
            node.material = new THREE.MeshPhongMaterial({ color: node.material.color });
        }
    }
    );
    gltf.scene.rotation.y = Math.PI / 2;
    gltf.scene.position.set(-1.6, -0.3, 0.2);
    scene.add(gltf.scene);
});

gltfLoader.load('/model/debris.glb', (gltf) => {
    gltf.scene.traverse((node) => {
        if (node.isMesh) {
            node.castShadow = true;
            node.receiveShadow = true;
            node.material = new THREE.MeshPhongMaterial({ color: node.material.color });
        }
    }
    );
    gltf.scene.rotation.y = Math.PI / 4;
    gltf.scene.position.set(0.2, -0.3, 0);
    scene.add(gltf.scene);
});

const iframe = document.createElement('iframe');
iframe.style.position = 'absolute';
iframe.style.border = 'none';
iframe.style.display = 'none';
iframe.src = '/';
document.body.appendChild(iframe);

const textureLoader = new THREE.TextureLoader();
const groundTexture = textureLoader.load('/texture/concrete.png');
groundTexture.wrapS = THREE.RepeatWrapping;
groundTexture.wrapT = THREE.RepeatWrapping;
groundTexture.repeat.set(10, 10);

const groundGeometry = new THREE.CircleGeometry(5, 32);
const groundMaterial = new THREE.MeshStandardMaterial({ map: groundTexture });
const groundMesh = new THREE.Mesh(groundGeometry, groundMaterial);
groundMesh.name = 'ground';
groundMesh.rotation.x = -Math.PI / 2;
groundMesh.position.y = -0.3;
groundMesh.receiveShadow = true;
scene.add(groundMesh);

const groundShape = new CANNON.Plane();
const groundBody = new CANNON.Body({ mass: 0 });
groundBody.addShape(groundShape);
groundBody.position.y = -0.3;
world.addBody(groundBody);
groundMesh.body = groundBody;
groundBody.quaternion.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), -Math.PI / 2);

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let selectedObject = null;

let lastCameraPosition = camera.position.clone();
let isLaptopOpen = false;
function onMouseDown(event) {
    if (isLaptopOpen) {
        closeLaptop();
        return;
    }
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    const objects = [];
    scene.traverse((object) => {
        if (object.isMesh) {
            objects.push(object);
        }
    });
    const intersects = raycaster.intersectObjects(objects, true);
    for (let i = 0; i < intersects.length; i++) {
        if (intersects[i].object.name === 'laptop') {
            openLaptop();
            break;
        }
        else if (intersects[i].object.name === 'file') {
            selectedObject = intersects[i].object;
            selectedObject.body.mass = 0;
            selectedObject.body.updateMassProperties();
            controls.enabled = false;
            break;
        }
    }
}

function onMouseUp() {
    if (selectedObject) {
        selectedObject.body.mass = 1;
        selectedObject.body.updateMassProperties();
        selectedObject = null;
        controls.enabled = true;
    }
}

function onMouseMove(event) {
    if (selectedObject) {
        selectedObject.body.quaternion.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), -Math.PI / 2);
        mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
        raycaster.setFromCamera(mouse, camera);
        let topDesk = scene.getObjectByName('topDesk');
        const intersectsTopDesk = raycaster.intersectObject(topDesk);
        let borderDesk = scene.getObjectByName('borderDesk');
        const intersectsBorderDesk = raycaster.intersectObject(borderDesk);
        let ground = scene.getObjectByName('ground');
        const intersectsGround = raycaster.intersectObject(ground);
        if (intersectsTopDesk.length > 0 || intersectsGround.length > 0) {
            selectedObject.body.angularVelocity.set(0, 0, 0);
            selectedObject.body.velocity.set(0, 0, 0);
            selectedObject.body.angularVelocity.set(0, 0, 0);
            if (intersectsTopDesk.length > 0) {
                selectedObject.body.position.copy(intersectsTopDesk[0].point);
            }
            else {
                if (intersectsBorderDesk.length > 0) {
                    return;
                }
                selectedObject.body.position.copy(intersectsGround[0].point);
            }
        }
    }
}

function getLaptopScreenSize() {
    let width, height;
    scene.traverse((object) => {
        if (object.isMesh && object.name === 'laptop') {
            if (object.material.name === 'blinn11SG') {
                let geometry = object.geometry;
                geometry.computeBoundingBox();

                let min = geometry.boundingBox.min.clone();
                let max = geometry.boundingBox.max.clone();

                object.updateMatrixWorld(true);
                min.applyMatrix4(object.matrixWorld);
                max.applyMatrix4(object.matrixWorld);

                min.project(camera);
                max.project(camera);

                width = Math.abs(max.x - min.x) * window.innerWidth / 1.9;
                height = Math.abs(max.y - min.y) * window.innerHeight / 1.9;
            }
        }
    });
    return { width, height };
}

function openLaptop() {
    lastCameraPosition = camera.position.clone();
    const targetPosition = { x: -0.809, y: 0.542, z: -0.066 };
    const targetRotation = { x: -0.048, y: 0.505, z: 0.03 };
    controls.enabled = false;
    new TWEEN.Tween(camera.position)
        .to(targetPosition, 2000)
        .easing(TWEEN.Easing.Quadratic.Out)
        .start();

    new TWEEN.Tween(camera.rotation)
        .to(targetRotation, 2000)
        .easing(TWEEN.Easing.Quadratic.Out)
        .onComplete(() => {
            iframe.style.display = 'block';
            let { width, height } = getLaptopScreenSize();
            iframe.style.width = `${width}px`;
            iframe.style.height = `${height}px`;
            iframe.style.top = `${window.innerHeight / 2 - height / 2}px`;
            iframe.style.left = `${window.innerWidth / 2 - width / 2}px`;
            isLaptopOpen = true;
        })
        .start();
}

function closeLaptop() {
    iframe.style.display = 'none';
    controls.enabled = true;
    new TWEEN.Tween(camera.position)
        .to(lastCameraPosition, 1000)
        .easing(TWEEN.Easing.Quadratic.Out)
        .onComplete(() => {
            isLaptopOpen = false;
        })
        .start();
}

window.addEventListener('mousedown', onMouseDown);
window.addEventListener('mouseup', onMouseUp);
window.addEventListener('mousemove', onMouseMove);

const socket = io.connect('/file_handler');

let desktopFiles = JSON.parse(localStorage.getItem('desktop'));
if (desktopFiles === null) {
    desktopFiles = [];
    localStorage.setItem('desktop', JSON.stringify(desktopFiles));
}
socket.emit('get_files_details', { files: desktopFiles });

socket.on('files_details', (data) => {
    data.forEach((file) => {
        createFileObject(file);
    });
});

const fontLoader = new FontLoader();
let font = null;
fontLoader.load('https://threejs.org/examples/fonts/helvetiker_regular.typeface.json', (response) => {
    font = response;
});
function createFileObject(file) {
    const fileGeometry = new THREE.BoxGeometry(0.15, 0.2, 0.025);
    const fileMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff });
    const fileMesh = new THREE.Mesh(fileGeometry, fileMaterial);
    fileMesh.position.set(Math.random() * 0.2 - 0.1, 1, Math.random() * 0.2 - 0.1);
    fileMesh.receiveShadow = true;
    fileMesh.castShadow = true;
    fileMesh.name = 'file';
    scene.add(fileMesh);

    const shapes = font.generateShapes(truncateString(file.nom_Fichier, file.nom_Fichier.length % 5, 4), 0.025);
    const geometry = new THREE.ShapeGeometry(shapes);
    geometry.computeBoundingBox();

    const xMid = - 0.5 * (geometry.boundingBox.max.x - geometry.boundingBox.min.x);
    geometry.translate(xMid, 0.06, 0);

    const textMaterial = new THREE.MeshBasicMaterial({ color: 0x000000 });
    const textMesh = new THREE.Mesh(geometry, textMaterial);
    textMesh.position.z = 0.013;
    fileMesh.add(textMesh);

    const fileShape = new CANNON.Box(new CANNON.Vec3(0.075, 0.1, 0.0125));
    const fileBody = new CANNON.Body({ mass: 1 });
    fileBody.addShape(fileShape);
    fileBody.position.set(fileMesh.position.x, fileMesh.position.y, fileMesh.position.z);
    fileBody.quaternion.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), -Math.PI / 2);
    world.addBody(fileBody);

    fileMesh.body = fileBody;
}

function truncateString(str, num, lineLength) {
    if (str.length > num) {
        let truncated = '';
        let lineCount = 0;
        let exceededLineLimit = false;
        for (let i = 0; i < str.length; i += lineLength) {
            if (lineCount < lineLength) {
                truncated += str.slice(i, i + lineLength) + '\n';
                lineCount++;
            } else {
                exceededLineLimit = true;
                break;
            }
        }
        return exceededLineLimit ? truncated.slice(0, truncated.length - 1) + '...' : truncated.slice(0, truncated.length - 1);
    } else {
        return str;
    }
}

function updatePhysics() {
    world.step(1 / 60);
    scene.traverse(function (object) {
        if (object.isMesh && object.body) {
            object.position.copy(object.body.position);
            object.quaternion.copy(object.body.quaternion);
        }
    });
}

function animate(time) {
    requestAnimationFrame(animate);
    if (controls.enabled) {
        controls.update();
    }
    updatePhysics();
    TWEEN.update(time);
    renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});