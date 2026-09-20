<template>
  <div class="card">
    <div class="card-header-flex">
      <h2 class="card-title" style="margin-bottom: 0;">
        <span>📝</span> Submit Information
      </h2>
      <span class="badge-role">Multi-Purpose Directory</span>
    </div>
    <p class="section-desc">Add a new record to your team, customer, vendor, or member directory.</p>

    <div v-if="successMsg" class="alert alert-success">
      ✅ {{ successMsg }}
    </div>
    <div v-if="errorMsg" class="alert alert-danger">
      ⚠️ {{ errorMsg }}
    </div>

    <form @submit.prevent="submitForm" class="form-grid">
      <!-- Row 1: Name and Category -->
      <div class="form-row-2">
        <div class="form-group">
          <label for="name">Full Name <span class="required">*</span></label>
          <input
            id="name"
            type="text"
            v-model.trim="name"
            placeholder="e.g. Alex Johnson"
            class="form-control"
            required
          />
        </div>

        <div class="form-group">
          <label for="category">Category / Purpose</label>
          <select id="category" v-model="category" class="form-control">
            <option value="General">General</option>
            <option value="Client">Client</option>
            <option value="Team Member">Team Member</option>
            <option value="Customer">Customer</option>
            <option value="Vendor">Vendor</option>
            <option value="Member">Member</option>
            <option value="Student">Student</option>
            <option value="VIP">VIP</option>
          </select>
        </div>
      </div>

      <!-- Row 2: Contact Number and Email -->
      <div class="form-row-2">
        <div class="form-group">
          <label for="contact">Contact Number <span class="required">*</span></label>
          <input
            id="contact"
            type="number"
            v-model.number="contact"
            placeholder="e.g. 9876543210"
            class="form-control"
            required
          />
        </div>

        <div class="form-group">
          <label for="email">Email Address <span class="optional">(Optional)</span></label>
          <input
            id="email"
            type="email"
            v-model.trim="email"
            placeholder="e.g. alex@example.com"
            class="form-control"
          />
        </div>
      </div>

      <!-- Address -->
      <div class="form-group">
        <label for="address">Address / Location <span class="required">*</span></label>
        <input
          id="address"
          type="text"
          v-model.trim="address"
          placeholder="e.g. 742 Evergreen Terrace, Sector 4"
          class="form-control"
          required
        />
      </div>

      <!-- Notes / Remarks -->
      <div class="form-group">
        <label for="notes">Notes & Additional Details <span class="optional">(Optional)</span></label>
        <textarea
          id="notes"
          v-model.trim="notes"
          placeholder="e.g. Department, project role, dietary requirements, or specific instructions..."
          rows="2"
          class="form-control textarea-control"
        ></textarea>
      </div>

      <!-- Photo Upload -->
      <div class="form-group">
        <label>Photo / Profile Image <span class="required">*</span></label>
        <div
          class="file-dropzone"
          :class="{ 'dropzone-active': isDragging }"
          @click="triggerFileInput"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="onFileDrop"
        >
          <input
            ref="fileInputRef"
            type="file"
            @change="onFileChange"
            accept="image/*"
            style="display: none;"
          />
          <div v-if="!image" class="dropzone-content">
            <span class="dropzone-icon">📷</span>
            <p class="dropzone-text"><strong>Click to upload</strong> or drag and drop image here</p>
            <span class="dropzone-hint">PNG, JPG, WEBP up to 10MB</span>
          </div>
          <div v-else class="dropzone-content">
            <span class="dropzone-icon">✅</span>
            <p class="dropzone-text"><strong>{{ image.name }}</strong> ({{ formatFileSize(image.size) }})</p>
            <span class="dropzone-hint">Click to choose a different photo</span>
          </div>
        </div>

        <div v-if="imagePreview" class="image-preview-container">
          <img :src="imagePreview" alt="Selected Preview" class="image-preview" />
          <div class="preview-actions">
            <span class="preview-label">Image Preview</span>
            <button type="button" @click="clearImage" class="btn-sm-danger">Remove photo</button>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="form-actions">
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          <span v-if="isSubmitting" class="btn-spinner"></span>
          <span v-if="isSubmitting">Saving Record...</span>
          <span v-else>➕ Save Entry</span>
        </button>
        <button type="button" @click="resetForm" class="btn-secondary" :disabled="isSubmitting">
          Reset
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref } from 'vue'
import { API_BASE_URL } from '../config'

const emit = defineEmits(['refresh'])

const name = ref("")
const category = ref("General")
const address = ref("")
const contact = ref("")
const email = ref("")
const notes = ref("")
const image = ref(null)
const imagePreview = ref("")
const fileInputRef = ref(null)

const isDragging = ref(false)
const isSubmitting = ref(false)
const successMsg = ref("")
const errorMsg = ref("")

function triggerFileInput() {
  fileInputRef.value?.click()
}

function processSelectedFile(file) {
  if (!file) return
  if (!file.type.startsWith('image/')) {
    errorMsg.value = "Please select a valid image file (PNG, JPG, WEBP)."
    return
  }
  image.value = file
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

function onFileChange(event) {
  const file = event.target.files?.[0]
  processSelectedFile(file)
}

function onFileDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer.files?.[0]
  processSelectedFile(file)
}

function formatFileSize(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function clearImage() {
  image.value = null
  imagePreview.value = ""
  if (fileInputRef.value) {
    fileInputRef.value.value = ""
  }
}

function resetForm() {
  name.value = ""
  category.value = "General"
  address.value = ""
  contact.value = ""
  email.value = ""
  notes.value = ""
  clearImage()
  errorMsg.value = ""
  successMsg.value = ""
}

const submitForm = async () => {
  successMsg.value = ""
  errorMsg.value = ""

  if (!name.value || !address.value || !contact.value || !image.value) {
    errorMsg.value = "Please fill in all required fields (Name, Contact, Address, Photo)."
    return
  }

  const formData = new FormData()
  formData.append("name", name.value)
  formData.append("address", address.value)
  formData.append("contact", contact.value)
  formData.append("category", category.value)
  if (email.value) formData.append("email", email.value)
  if (notes.value) formData.append("notes", notes.value)
  formData.append("image", image.value)

  isSubmitting.value = true
  try {
    const endpoint = `${API_BASE_URL}/submit/`
    await axios.post(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    resetForm()
    successMsg.value = "Record saved successfully to directory!"
    emit('refresh')
  } catch (error) {
    console.error("Error saving data:", error)
    const detail = error.response?.data?.detail || error.message || "Failed to save record."
    errorMsg.value = `Error: ${detail}`
  } finally {
    isSubmitting.value = false
  }
}
</script>
