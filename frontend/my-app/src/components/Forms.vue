<template>
  <div>
    <h2 class="header">Submit Your Details</h2>
    <form @submit.prevent="submitForm" class="submit-form">  
      <input type="text" v-model="Name" placeholder="Name" required /><br>
      <input type="text" v-model="Address" placeholder="Address" required /><br>
      <input type="number" v-model="Contact" placeholder="Contact" required /><br>
      <div class="image-upload">
        <input type="file" @change="onFileChange" accept="image/*" />
      </div>
      <img v-if="ImagePreview" :src="ImagePreview" alt="Selected Image"
           style="object-fit: cover; max-width: 100px; max-height: 120px;" /><br>
      <button class="button" type="submit">Submit</button>
    </form>
  </div>
</template>

<script setup>


import axios from 'axios'
import { ref } from 'vue'

const emit = defineEmits(['refresh'])

const Name = ref("")
const Address = ref("")
const Contact = ref("")
const Image = ref(null)
const ImagePreview = ref("")

function onFileChange(event) {
  const file = event.target.files[0]
  if (file) {
    Image.value = file
    const reader = new FileReader()
    reader.onload = (e) => {
      ImagePreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const submitForm = async () => {
  const form_Data = new FormData()
  form_Data.append("name", Name.value)
  form_Data.append("address", Address.value)
  form_Data.append("contact", Contact.value)
  form_Data.append("image", Image.value)

  if (!Name.value || !Address.value || !Contact.value || !Image.value) {
    alert("Please fill in all fields and select an image.")
    return
  }
  try {
    await axios.post("https://info-form-production.up.railway.app/", form_Data, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    Name.value = ""
    Address.value = ""
    Contact.value = ""
    Image.value = null
    ImagePreview.value = ""
    emit('refresh')
    alert('Data saved successfully!')
  } catch (error) {
    console.error("Error saving data:", error)
    alert("Failed to save data.")
  }
  
}
</script>

<style scoped>
.header {
  text-align: center;
  font-size: 24px;
  margin-bottom: 20px;
}

.image-upload {
  margin-left: 35%;
}

.button {
  padding: 5px 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
}

.submit-form {
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>
