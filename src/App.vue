<template>
  <div class="app-container">
    <!-- Top Navigation & Brand Header -->
    <header class="app-header">
      <div class="header-main-row">
        <div class="brand-block">
          <div class="brand-logo-icon">📇</div>
          <div>
            <h1 class="brand-title">PulseDesk</h1>
            <p class="brand-tagline">Universal Directory & Contact Management Hub</p>
          </div>
        </div>

        <!-- Live Status & Purpose Tags -->
        <div class="header-badges-row">
          <span class="status-indicator-badge">
            <span class="pulse-dot"></span> Ready & Syncing
          </span>
          <button 
            type="button" 
            @click="isMascotVisible = !isMascotVisible" 
            class="mascot-toggle-btn"
            :title="isMascotVisible ? 'Minimize 3D Mascot' : 'Show 3D Companion Mascot'"
          >
            <span>{{ isMascotVisible ? '🤖 Hide Mascot' : '✨ Show 3D Mascot' }}</span>
          </button>
        </div>
      </div>

      <!-- Quick Purpose Presets Switcher -->
      <div class="presets-banner">
        <span class="presets-intro">🎯 Purpose Presets:</span>
        <div class="preset-buttons-group">
          <button
            v-for="preset in DIRECTORY_PRESETS"
            :key="preset.id"
            type="button"
            class="preset-chip"
            :class="{ 'preset-chip-active': activePresetId === preset.id }"
            @click="selectPreset(preset)"
            :title="preset.description"
          >
            <span>{{ preset.icon }}</span> {{ preset.name }}
          </button>
        </div>
      </div>
    </header>

    <!-- 3D Cute Interactive Companion Mascot Stage (Collapsible) -->
    <transition name="slide-fade">
      <div v-show="isMascotVisible" class="mascot-section-wrapper">
        <CuteCompanion3D ref="mascotRef" />
      </div>
    </transition>

    <!-- Main Content Workspace -->
    <main class="main-workspace">
      <Form ref="formComponent" @refresh="onFormSubmitted" />
      <Records ref="recordsComponent" />
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <p>PulseDesk · Multi-purpose Contact & Directory Management Hub</p>
      <p class="footer-sub">FastAPI Serverless & MongoDB Backend · Vue 3 & Three.js Single Page App</p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Form from './components/Forms.vue'
import Records from './components/Records.vue'
import CuteCompanion3D from './components/CuteCompanion3D.vue'
import { DIRECTORY_PRESETS } from './dummyData'

const recordsComponent = ref(null)
const formComponent = ref(null)
const mascotRef = ref(null)
const isMascotVisible = ref(true)
const activePresetId = ref('crm')

const selectPreset = (preset) => {
  activePresetId.value = preset.id
  if (recordsComponent.value) {
    recordsComponent.value.selectedCategory = preset.defaultCategory
  }
  if (formComponent.value) {
    formComponent.value.category = preset.defaultCategory
  }
}

const onFormSubmitted = () => {
  // Trigger 3D mascot celebration dance + confetti
  mascotRef.value?.celebrateSubmission?.()

  // Refresh records table
  if (recordsComponent.value?.loadRecords) {
    recordsComponent.value.loadRecords()
  }
}
</script>
