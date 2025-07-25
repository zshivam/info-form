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
  const res =await axios.get("http://127.0.0.1:8000/records/");

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
