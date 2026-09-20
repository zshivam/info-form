<template>
  <div class="cute-3d-stage-container" :class="{ 'party-active': isPartyMode }">
    <!-- Speech bubble -->
    <transition name="pop">
      <div v-if="speechText" class="speech-bubble">
        <span class="speech-emoji">{{ currentEmoji }}</span>
        <span class="speech-content">{{ speechText }}</span>
        <div class="speech-arrow"></div>
      </div>
    </transition>

    <!-- 3D Canvas Stage -->
    <div
      ref="canvasContainer"
      class="three-canvas-box"
      @click="handleMascotClick"
      title="Click me to poke, bounce, or change my hat!"
    >
      <div class="mascot-tag">
        <span>✨ POKE ME!</span>
      </div>
    </div>

    <!-- Interactive Funny Controls -->
    <div class="mascot-controls">
      <button @click.stop="triggerBounce" class="mascot-btn" title="Make me bounce!">
        🎾 Bounce
      </button>
      <button @click.stop="cycleHat" class="mascot-btn" title="Change my hat!">
        🎩 Hat: {{ currentHatName }}
      </button>
      <button
        @click.stop="togglePartyMode"
        class="mascot-btn party-btn"
        :class="{ 'party-btn-on': isPartyMode }"
        title="Trigger crazy disco party mode!"
      >
        🪩 {{ isPartyMode ? 'Party Active!' : 'Disco Mode' }}
      </button>
      <button @click.stop="surpriseBurst" class="mascot-btn surprise-btn" title="Surprise me!">
        🎁 Surprise!
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as THREE from 'three'
import confetti from 'canvas-confetti'

const canvasContainer = ref(null)
const speechText = ref("Hi! I'm Blobby! Click me for surprises ✨")
const currentEmoji = ref("👋")
const isPartyMode = ref(false)
const currentHatIndex = ref(0)
const currentHatName = ref("Party Hat")

const quotes = [
  { text: "Boop! Hey, that tickles! 😆", emoji: "✨" },
  { text: "Did you submit your details yet? I'm watching 👀", emoji: "📝" },
  { text: "Look ma, I'm fully 3D! 🕶️", emoji: "✨" },
  { text: "10/10 best form filler ever! 🏆", emoji: "⭐" },
  { text: "Wheeeeee! Jelly physics activate! 🍮", emoji: "🚀" },
  { text: "Error 404: Seriousness not found! 🤪", emoji: "🎈" },
  { text: "I like your cursor moves! Very stylish! 💃", emoji: "💖" },
  { text: "Secret unlocked: You are awesome! 🌟", emoji: "🎉" },
]

let speechTimer = null
function speak(text, emoji = "💬", duration = 3200) {
  speechText.value = text
  currentEmoji.value = emoji
  if (speechTimer) clearTimeout(speechTimer)
  speechTimer = setTimeout(() => {
    speechText.value = ""
  }, duration)
}

// Three.js State
let scene, camera, renderer, animationFrameId
let mascotGroup, bodyMesh, leftEye, rightEye, leftPupil, rightPupil
let leftCheek, rightCheek, mouthMesh
let leftEar, rightEar
let hatGroup = null
let floatingSurprises = []
let discoLight1, discoLight2

// Animation variables
let targetMouseX = 0
let targetMouseY = 0
let currentMouseX = 0
let currentMouseY = 0
let bounceScale = { x: 1, y: 1, z: 1 }
let bounceVelocity = 0
let jumpY = 0
let jumpVelocity = 0
let rotVelocity = 0
let partyHue = 0

// Hats definition
const hats = [
  { name: "Party Hat", type: "cone" },
  { name: "Crown", type: "crown" },
  { name: "Cool Shades", type: "glasses" },
  { name: "Mustache", type: "mustache" },
  { name: "Donut", type: "donut" },
  { name: "None", type: "none" }
]

function initThree() {
  const container = canvasContainer.value
  if (!container) return

  const width = container.clientWidth || 320
  const height = 240

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 1000)
  camera.position.set(0, 0, 7)

  renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  container.appendChild(renderer.domElement)

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 1.2)
  scene.add(ambientLight)

  const dirLight = new THREE.DirectionalLight(0xfff3e0, 1.8)
  dirLight.position.set(5, 8, 5)
  scene.add(dirLight)

  const backLight = new THREE.PointLight(0x818cf8, 2, 12)
  backLight.position.set(-4, -2, -2)
  scene.add(backLight)

  // Disco lights (active in party mode)
  discoLight1 = new THREE.PointLight(0xff007f, 0, 15)
  discoLight1.position.set(3, 3, 2)
  scene.add(discoLight1)

  discoLight2 = new THREE.PointLight(0x00f5ff, 0, 15)
  discoLight2.position.set(-3, -2, 2)
  scene.add(discoLight2)

  // Create Mascot
  createMascot()

  // Create Background Floating Fun Elements (Donuts, stars, gems)
  createFloatingItems()

  // Setup Hat
  updateHat()

  // Event Listeners
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('resize', onWindowResize)

  animate()
}

function createMascot() {
  mascotGroup = new THREE.Group()
  scene.add(mascotGroup)

  // 1. Squishy Cute Body (Subdivided Icosahedron / Sphere)
  const bodyGeo = new THREE.SphereGeometry(1.3, 36, 36)
  const bodyMat = new THREE.MeshStandardMaterial({
    color: 0xffd166, // Warm pastel golden honey
    roughness: 0.25,
    metalness: 0.1,
  })
  bodyMesh = new THREE.Mesh(bodyGeo, bodyMat)
  bodyMesh.castShadow = true
  mascotGroup.add(bodyMesh)

  // 2. Big Kawaii Eyes
  const eyeGeo = new THREE.SphereGeometry(0.22, 24, 24)
  const eyeMat = new THREE.MeshBasicMaterial({ color: 0xffffff })

  leftEye = new THREE.Mesh(eyeGeo, eyeMat)
  leftEye.position.set(-0.45, 0.2, 1.1)
  mascotGroup.add(leftEye)

  rightEye = new THREE.Mesh(eyeGeo, eyeMat)
  rightEye.position.set(0.45, 0.2, 1.1)
  mascotGroup.add(rightEye)

  // Pupils
  const pupilGeo = new THREE.SphereGeometry(0.12, 16, 16)
  const pupilMat = new THREE.MeshBasicMaterial({ color: 0x111827 })

  leftPupil = new THREE.Mesh(pupilGeo, pupilMat)
  leftPupil.position.set(0, 0, 0.12)
  leftEye.add(leftPupil)

  rightPupil = new THREE.Mesh(pupilGeo, pupilMat)
  rightPupil.position.set(0, 0, 0.12)
  rightEye.add(rightPupil)

  // Pupil sparkles
  const sparkleGeo = new THREE.SphereGeometry(0.04, 8, 8)
  const sparkleMat = new THREE.MeshBasicMaterial({ color: 0xffffff })
  const leftSparkle = new THREE.Mesh(sparkleGeo, sparkleMat)
  leftSparkle.position.set(0.04, 0.04, 0.08)
  leftPupil.add(leftSparkle)

  const rightSparkle = new THREE.Mesh(sparkleGeo, sparkleMat)
  rightSparkle.position.set(0.04, 0.04, 0.08)
  rightPupil.add(rightSparkle)

  // 3. Rosy Blushing Cheeks
  const cheekGeo = new THREE.SphereGeometry(0.16, 16, 16)
  const cheekMat = new THREE.MeshStandardMaterial({
    color: 0xff5d8f,
    roughness: 0.5,
    transparent: true,
    opacity: 0.8
  })

  leftCheek = new THREE.Mesh(cheekGeo, cheekMat)
  leftCheek.position.set(-0.75, -0.05, 0.95)
  leftCheek.scale.set(1.2, 0.6, 0.5)
  mascotGroup.add(leftCheek)

  rightCheek = new THREE.Mesh(cheekGeo, cheekMat)
  rightCheek.position.set(0.75, -0.05, 0.95)
  rightCheek.scale.set(1.2, 0.6, 0.5)
  mascotGroup.add(rightCheek)

  // 4. Cute Cat/Bunny Ears
  const earGeo = new THREE.ConeGeometry(0.35, 0.8, 20)
  const earMat = new THREE.MeshStandardMaterial({
    color: 0xffa07a,
    roughness: 0.3
  })

  leftEar = new THREE.Mesh(earGeo, earMat)
  leftEar.position.set(-0.75, 1.35, 0)
  leftEar.rotation.z = 0.25
  mascotGroup.add(leftEar)

  rightEar = new THREE.Mesh(earGeo, earMat)
  rightEar.position.set(0.75, 1.35, 0)
  rightEar.rotation.z = -0.25
  mascotGroup.add(rightEar)

  // 5. Smiling Mouth
  const mouthCurve = new THREE.CubicBezierCurve3(
    new THREE.Vector3(-0.2, 0, 0),
    new THREE.Vector3(-0.1, -0.15, 0),
    new THREE.Vector3(0.1, -0.15, 0),
    new THREE.Vector3(0.2, 0, 0)
  )
  const mouthGeo = new THREE.TubeGeometry(mouthCurve, 16, 0.035, 8, false)
  const mouthMat = new THREE.MeshBasicMaterial({ color: 0x6b21a8 })
  mouthMesh = new THREE.Mesh(mouthGeo, mouthMat)
  mouthMesh.position.set(0, -0.15, 1.25)
  mascotGroup.add(mouthMesh)

  // Hat mount group
  hatGroup = new THREE.Group()
  hatGroup.position.set(0, 1.3, 0)
  mascotGroup.add(hatGroup)
}

function createFloatingItems() {
  // Floating colorful little items in the background
  const geometries = [
    new THREE.TorusGeometry(0.3, 0.12, 16, 24), // Donut
    new THREE.OctahedronGeometry(0.28),         // Diamond / Gem
    new THREE.SphereGeometry(0.25, 16, 16),      // Bubble
    new THREE.TetrahedronGeometry(0.3)          // Star pyramid
  ]

  const colors = [0x60a5fa, 0xf472b6, 0x34d399, 0xfbbf24, 0xa78bfa]

  for (let i = 0; i < 7; i++) {
    const geo = geometries[i % geometries.length]
    const mat = new THREE.MeshStandardMaterial({
      color: colors[i % colors.length],
      roughness: 0.2,
      metalness: 0.15
    })
    const mesh = new THREE.Mesh(geo, mat)
    mesh.position.set(
      (Math.random() - 0.5) * 7,
      (Math.random() - 0.5) * 4,
      (Math.random() - 0.5) * 3 - 2
    )
    mesh.userData = {
      baseY: mesh.position.y,
      speed: 0.5 + Math.random() * 1.5,
      rotX: (Math.random() - 0.5) * 0.03,
      rotY: (Math.random() - 0.5) * 0.03,
      floatOffset: Math.random() * Math.PI * 2
    }
    scene.add(mesh)
    floatingSurprises.push(mesh)
  }
}

function updateHat() {
  if (!hatGroup) return
  // Clear old hat meshes
  while (hatGroup.children.length > 0) {
    hatGroup.remove(hatGroup.children[0])
  }

  const current = hats[currentHatIndex.value]
  currentHatName.value = current.name

  if (current.type === "cone") {
    // Party Cone Hat
    const coneGeo = new THREE.ConeGeometry(0.45, 0.9, 20)
    const coneMat = new THREE.MeshStandardMaterial({
      color: 0xef4444,
      roughness: 0.3
    })
    const cone = new THREE.Mesh(coneGeo, coneMat)
    cone.position.set(0, 0.35, 0)
    cone.rotation.z = -0.15

    // Pom pom on top
    const pomGeo = new THREE.SphereGeometry(0.12, 12, 12)
    const pomMat = new THREE.MeshBasicMaterial({ color: 0xfef08a })
    const pom = new THREE.Mesh(pomGeo, pomMat)
    pom.position.set(0, 0.45, 0)
    cone.add(pom)

    hatGroup.add(cone)
  } else if (current.type === "crown") {
    // Royal Golden Crown
    const crownGeo = new THREE.CylinderGeometry(0.55, 0.4, 0.4, 5, 1, true)
    const crownMat = new THREE.MeshStandardMaterial({
      color: 0xf59e0b,
      metalness: 0.7,
      roughness: 0.2
    })
    const crown = new THREE.Mesh(crownGeo, crownMat)
    crown.position.set(0, 0.1, 0)
    hatGroup.add(crown)
  } else if (current.type === "glasses") {
    // Cool 3D Sunglasses
    const glassesGroup = new THREE.Group()
    glassesGroup.position.set(0, -1.05, 1.25)

    const glassMat = new THREE.MeshBasicMaterial({ color: 0x111827 })
    const leftGlass = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.25, 0.08), glassMat)
    leftGlass.position.set(-0.45, 0, 0)
    glassesGroup.add(leftGlass)

    const rightGlass = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.25, 0.08), glassMat)
    rightGlass.position.set(0.45, 0, 0)
    glassesGroup.add(rightGlass)

    const bridge = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.05, 0.08), glassMat)
    bridge.position.set(0, 0.05, 0)
    glassesGroup.add(bridge)

    hatGroup.add(glassesGroup)
  } else if (current.type === "mustache") {
    // Funny Curly Mustache
    const mustGroup = new THREE.Group()
    mustGroup.position.set(0, -1.35, 1.3)
    const mustMat = new THREE.MeshStandardMaterial({ color: 0x1f2937 })
    const mLeft = new THREE.Mesh(new THREE.TorusGeometry(0.18, 0.08, 12, 16, Math.PI), mustMat)
    mLeft.position.set(-0.2, 0, 0)
    mLeft.rotation.z = Math.PI
    mustGroup.add(mLeft)

    const mRight = new THREE.Mesh(new THREE.TorusGeometry(0.18, 0.08, 12, 16, Math.PI), mustMat)
    mRight.position.set(0.2, 0, 0)
    mRight.rotation.z = Math.PI
    mustGroup.add(mRight)

    hatGroup.add(mustGroup)
  } else if (current.type === "donut") {
    // Giant Donut on head
    const donutGeo = new THREE.TorusGeometry(0.55, 0.22, 16, 28)
    const donutMat = new THREE.MeshStandardMaterial({
      color: 0xf472b6,
      roughness: 0.3
    })
    const donut = new THREE.Mesh(donutGeo, donutMat)
    donut.position.set(0, 0.2, 0)
    donut.rotation.x = Math.PI / 2
    hatGroup.add(donut)
  }
}

function cycleHat() {
  currentHatIndex.value = (currentHatIndex.value + 1) % hats.length
  updateHat()
  triggerBounce()
  speak(`Changed hat to: ${currentHatName.value}! 🎩`, "✨", 2200)
}

function onMouseMove(event) {
  const normX = (event.clientX / window.innerWidth) * 2 - 1
  const normY = -(event.clientY / window.innerHeight) * 2 + 1
  targetMouseX = normX
  targetMouseY = normY
}

function onWindowResize() {
  if (!canvasContainer.value || !camera || !renderer) return
  const width = canvasContainer.value.clientWidth || 320
  const height = 240
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

function handleMascotClick() {
  triggerBounce()
  const randomPick = quotes[Math.floor(Math.random() * quotes.length)]
  speak(randomPick.text, randomPick.emoji)

  // Confetti burst from click
  confetti({
    particleCount: 28,
    spread: 55,
    origin: { y: 0.3 }
  })
}

function triggerBounce() {
  // Squish and bounce animation
  bounceScale = { x: 1.35, y: 0.65, z: 1.35 }
  bounceVelocity = 0.1
  jumpVelocity = 0.18
  rotVelocity = (Math.random() - 0.5) * 0.4
}

function togglePartyMode() {
  isPartyMode.value = !isPartyMode.value
  if (isPartyMode.value) {
    discoLight1.intensity = 4
    discoLight2.intensity = 4
    speak("🎉 DISCO PARTY ACTIVATED! 🎉", "🪩", 4000)
    confetti({
      particleCount: 80,
      spread: 100,
      origin: { y: 0.4 }
    })
  } else {
    discoLight1.intensity = 0
    discoLight2.intensity = 0
    bodyMesh.material.color.setHex(0xffd166)
    speak("Party paused! Back to business 📋", "😌", 2500)
  }
}

function surpriseBurst() {
  triggerBounce()
  speak("🎊 TA-DA! Super surprise celebration! 🎊", "🎁", 3500)
  confetti({
    particleCount: 120,
    spread: 120,
    origin: { y: 0.35 }
  })
}

// Global celebration trigger (callable by parent when form is submitted!)
function celebrateSubmission() {
  triggerBounce()
  jumpVelocity = 0.28
  rotVelocity = Math.PI * 2
  speak("🎉 RECORD SAVED! High five! You are awesome! 🥳", "🚀", 5000)
  confetti({
    particleCount: 150,
    spread: 140,
    origin: { y: 0.4 }
  })
}

defineExpose({
  celebrateSubmission,
  triggerBounce,
  speak
})

function animate() {
  animationFrameId = requestAnimationFrame(animate)

  // Smooth mouse look
  currentMouseX += (targetMouseX - currentMouseX) * 0.08
  currentMouseY += (targetMouseY - currentMouseY) * 0.08

  const time = performance.now() * 0.003

  // Mascot head/body slight tilting towards cursor
  if (mascotGroup) {
    mascotGroup.rotation.y = currentMouseX * 0.5 + Math.sin(time) * 0.05
    mascotGroup.rotation.x = -currentMouseY * 0.3

    // Ears wobble
    if (leftEar && rightEar) {
      leftEar.rotation.z = 0.25 + Math.sin(time * 2) * 0.08
      rightEar.rotation.z = -0.25 - Math.sin(time * 2) * 0.08
    }

    // Pupils follow mouse precisely
    const pupilRange = 0.08
    if (leftPupil && rightPupil) {
      leftPupil.position.x = currentMouseX * pupilRange
      leftPupil.position.y = currentMouseY * pupilRange
      rightPupil.position.x = currentMouseX * pupilRange
      rightPupil.position.y = currentMouseY * pupilRange
    }

    // Bounce & Squish Spring Physics
    bounceScale.x += (1.0 - bounceScale.x) * 0.15
    bounceScale.y += (1.0 - bounceScale.y) * 0.15
    bounceScale.z += (1.0 - bounceScale.z) * 0.15

    jumpY += jumpVelocity
    if (jumpY > 0) {
      jumpVelocity -= 0.015
    } else {
      jumpY = 0
      jumpVelocity = 0
    }

    mascotGroup.scale.set(bounceScale.x, bounceScale.y, bounceScale.z)
    mascotGroup.position.y = Math.sin(time * 1.5) * 0.12 + jumpY

    if (rotVelocity > 0.01) {
      mascotGroup.rotation.y += rotVelocity
      rotVelocity *= 0.92
    }

    // Party Mode animations
    if (isPartyMode.value) {
      partyHue = (partyHue + 0.015) % 1
      const discoColor = new THREE.Color().setHSL(partyHue, 0.9, 0.6)
      bodyMesh.material.color.copy(discoColor)

      discoLight1.color.setHSL((partyHue + 0.3) % 1, 1, 0.5)
      discoLight2.color.setHSL((partyHue + 0.7) % 1, 1, 0.5)

      mascotGroup.rotation.z = Math.sin(time * 8) * 0.15
      mascotGroup.position.y += Math.abs(Math.sin(time * 8)) * 0.25
    }
  }

  // Animate floating surprise items
  floatingSurprises.forEach(mesh => {
    mesh.rotation.x += mesh.userData.rotX
    mesh.rotation.y += mesh.userData.rotY
    mesh.position.y = mesh.userData.baseY + Math.sin(time * mesh.userData.speed + mesh.userData.floatOffset) * 0.35
    // React slightly to mouse parallax
    mesh.position.x += (targetMouseX * 0.5 - mesh.position.x * 0.05) * 0.01
  })

  if (renderer && scene && camera) {
    renderer.render(scene, camera)
  }
}

onMounted(() => {
  initThree()
})

onBeforeUnmount(() => {
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('resize', onWindowResize)
  if (renderer) renderer.dispose()
})
</script>

<style scoped>
.cute-3d-stage-container {
  position: relative;
  background: linear-gradient(135deg, #fef3c7 0%, #ede9fe 50%, #e0e7ff 100%);
  border: 2px dashed #c7d2fe;
  border-radius: var(--radius-lg);
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
  overflow: visible;
}

.cute-3d-stage-container:hover {
  border-color: var(--primary);
  box-shadow: var(--shadow-md);
}

.party-active {
  background: linear-gradient(135deg, #fbcfe8 0%, #fed7aa 25%, #fef08a 50%, #a7f3d0 75%, #bae6fd 100%);
  animation: rainbowBorder 2s linear infinite;
  box-shadow: 0 0 25px rgba(236, 72, 153, 0.35);
}

@keyframes rainbowBorder {
  0% { border-color: #f43f5e; }
  25% { border-color: #8b5cf6; }
  50% { border-color: #06b6d4; }
  75% { border-color: #10b981; }
  100% { border-color: #f43f5e; }
}

/* Speech Bubble */
.speech-bubble {
  position: absolute;
  top: -1.75rem;
  background: #ffffff;
  border: 2px solid #818cf8;
  color: #1e1b4b;
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  font-size: 0.9rem;
  font-weight: 700;
  box-shadow: 0 8px 16px rgba(99, 102, 241, 0.15);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  z-index: 10;
  pointer-events: none;
  white-space: nowrap;
}

.speech-emoji {
  font-size: 1.2rem;
}

.speech-arrow {
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 8px solid #818cf8;
}

/* Canvas container */
.three-canvas-box {
  width: 100%;
  max-width: 380px;
  height: 220px;
  cursor: grab;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.three-canvas-box:active {
  cursor: grabbing;
}

.mascot-tag {
  position: absolute;
  bottom: 0.25rem;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(4px);
  border: 1px solid #e2e8f0;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--primary);
  letter-spacing: 0.05em;
  pointer-events: none;
  animation: pulseTag 2s infinite ease-in-out;
}

@keyframes pulseTag {
  0%, 100% { transform: scale(1); opacity: 0.9; }
  50% { transform: scale(1.06); opacity: 1; }
}

/* Controls */
.mascot-controls {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 0.5rem;
}

.mascot-btn {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #334155;
  padding: 0.4rem 0.85rem;
  border-radius: 9999px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.mascot-btn:hover {
  background: #f8fafc;
  border-color: var(--primary);
  color: var(--primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
}

.party-btn {
  background: #ede9fe;
  color: #6d28d9;
  border-color: #ddd6fe;
}

.party-btn:hover,
.party-btn-on {
  background: #7c3aed;
  color: #ffffff;
  border-color: #6d28d9;
}

.surprise-btn {
  background: #fdf2f8;
  color: #be185d;
  border-color: #fbcfe8;
}

.surprise-btn:hover {
  background: #f43f5e;
  color: #ffffff;
}

/* Transitions */
.pop-enter-active,
.pop-leave-active {
  transition: all 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.85);
}
</style>
