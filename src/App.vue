<template>
  <div class="app-container">
    <!-- Top Navigation & Brand Header -->
    <header class="app-header">
      <div class="header-main-row">
        <div class="brand-block">
          <div class="brand-logo-icon">📋</div>
          <div>
            <h1 class="brand-title">PulseDesk</h1>
            <p class="brand-tagline">Professional Directory & Form Management System</p>
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
      <p><strong>PulseDesk</strong> · Professional Contact & Directory Management System</p>
      <p class="footer-sub">Secure Enterprise Form Submission & Record Storage</p>
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
