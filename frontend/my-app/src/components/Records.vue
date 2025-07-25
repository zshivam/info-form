<template>
  <div>
  
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'

const Records = ref([])

const loadRecords = async () => {
  try{
  const res =await axios.get("railway link -p 66c8b3fa-c0c7-40ca-a176-2a62c3f23c0d");

  Records.value = res.data
  } catch (error) {
    console.error('Error loading records:', error)
  }
} 

onMounted(() => {
  loadRecords()
})

defineExpose({
   loadRecords })
</script>
