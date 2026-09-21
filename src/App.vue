<template>
  <div class="app-container">
    <header class="app-header">
      <div class="logo-badge">📋</div>
      <h1>Info Form System</h1>
      <p class="subtitle">Submit information with image upload and view saved records</p>
    </header>

    <!-- 3D Cute Funny Mascot Stage with Surprising Elements -->
    <CuteCompanion3D ref="mascotRef" />

    <main style="display: flex; flex-direction: column; gap: 2rem;">
      <Form @refresh="onFormSubmitted" />
      <Records ref="recordsComponent" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Form from './components/Forms.vue'
import Records from './components/Records.vue'
import CuteCompanion3D from './components/CuteCompanion3D.vue'

const recordsComponent = ref(null)
const mascotRef = ref(null)

const onFormSubmitted = () => {
  // Trigger cute 3D mascot celebration dance + confetti
  mascotRef.value?.celebrateSubmission?.()

  // Refresh records table
  if (recordsComponent.value?.loadRecords) {
    recordsComponent.value.loadRecords()
  } else if (recordsComponent.value?.loadData) {
    recordsComponent.value.loadData()
  }
}

const loadRecords = () => {
  if (recordsComponent.value?.loadRecords) {
    recordsComponent.value.loadRecords()
  } else if (recordsComponent.value?.loadData) {
    recordsComponent.value.loadData()
  }
}
</script>

