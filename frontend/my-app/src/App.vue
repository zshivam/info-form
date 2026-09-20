<template>
  <div class="app-container">
    <header class="app-header">
      <div class="logo-badge">📋</div>
      <h1>Info Form System</h1>
      <p class="subtitle">Submit information with image upload and view saved records</p>
    </header>

    <main style="display: flex; flex-direction: column; gap: 2rem;">
      <Form @refresh="loadRecords" />
      <Records ref="recordsComponent" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Form from './components/Forms.vue'
import Records from './components/Records.vue'

const recordsComponent = ref(null)

const loadRecords = () => {
  if (recordsComponent.value?.loadRecords) {
    recordsComponent.value.loadRecords()
  } else if (recordsComponent.value?.loadData) {
    recordsComponent.value.loadData()
  }
}
</script>
