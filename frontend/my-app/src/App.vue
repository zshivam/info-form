<template>
  <div>
    <Form @refresh="loadRecords" />
    <Records ref="recordsComponent" />
  </div>
</template>

<script setup>
import {ref} from 'vue'
import Form from './components/Forms.vue'
import Records from './components/Records.vue'

const recordsComponent = ref(null)

const loadRecords = () => {
  recordsComponent.value?.loadData?.()
}
</script>
