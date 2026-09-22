<template>
  <div class="app-container">
    <!-- Top Navigation & Brand Header -->
    <header class="app-header">
      <div class="header-main-row">
        <div class="brand-block">
          <div class="brand-logo-icon">
            <!-- Custom inFOrm SVG Logo blending Info ('i') and Form ('F' lines) around 'fo' -->
            <svg class="brand-svg-logo" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="36" height="36" rx="9" fill="url(#inFOrmGrad)" />
              <!-- Info Dot & Stem ('i') -->
              <circle cx="11.5" cy="11" r="2.2" fill="#ffffff" />
              <path d="M11.5 16.5V25" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" />
              <!-- Form Checklist Lines ('form') -->
              <path d="M17.5 12H25M17.5 17.5H25M17.5 23H22" stroke="#bfdbfe" stroke-width="2.2" stroke-linecap="round" />
              <defs>
                <linearGradient id="inFOrmGrad" x1="0" y1="0" x2="36" y2="36" gradientUnits="userSpaceOnUse">
                  <stop stop-color="#2563eb" />
                  <stop offset="1" stop-color="#1d4ed8" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div>
            <h1 class="brand-title">in<span class="brand-fo">fo</span>rm</h1>
            <p class="brand-tagline">Where Information Takes Form · Smart Directory Hub</p>
          </div>
        </div>

        <!-- Live Status & Mode Badges -->
        <div class="header-badges-row">
          <span class="status-indicator-badge">
            <span class="pulse-dot"></span> System Online
          </span>
          <span class="system-mode-badge">
            <span>🛡️</span> Verified Production
          </span>
        </div>
      </div>

      <!-- Quick Purpose Presets Switcher -->
      <div class="presets-banner">
        <span class="presets-intro">Select Preset:</span>
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

    <!-- Main Content Workspace -->
    <main class="main-workspace">
      <Form ref="formComponent" @refresh="onFormSubmitted" />
      <Records ref="recordsComponent" />
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <p><strong>in<span class="brand-fo">fo</span>rm</strong> · Where Information Takes Form</p>
      <p class="footer-sub">Enterprise Contact & Directory Form Engine · FastAPI & MongoDB</p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Form from './components/Forms.vue'
import Records from './components/Records.vue'
import { DIRECTORY_PRESETS } from './dummyData'

const recordsComponent = ref(null)
const formComponent = ref(null)
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
  // Refresh records table
  if (recordsComponent.value?.loadRecords) {
    recordsComponent.value.loadRecords()
  }
}
</script>
