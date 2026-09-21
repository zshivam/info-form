<template>
  <div class="card form-card">
    <!-- Form Header & Quick Tools -->
    <div class="card-header-flex">
      <div>
        <h2 class="card-title">
          <span class="header-icon">✍️</span> Add Directory Entry
        </h2>
        <p class="section-desc">
          Capture client leads, team members, event guests, or vendor details with instant photo sync.
        </p>
      </div>
      <div class="header-tools">
        <button 
          type="button" 
          @click="fillDemoRecord" 
          class="btn-demo-autofill"
          title="Autofill realistic sample data to test the form immediately"
        >
          <span>✨</span> Try Demo Record
        </button>
      </div>
    </div>

    <!-- Alert Notifications -->
    <transition name="fade">
      <div v-if="successMsg" class="alert alert-success">
        <div class="alert-content">
          <span class="alert-icon">🎉</span>
          <div>
            <strong>Entry Created Successfully!</strong>
            <p>{{ successMsg }}</p>
          </div>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="errorMsg" class="alert alert-danger">
        <div class="alert-content">
          <span class="alert-icon">⚠️</span>
          <div>
            <strong>Submission Error</strong>
            <p>{{ errorMsg }}</p>
          </div>
        </div>
      </div>
    </transition>

    <!-- Submission Form -->
    <form @submit.prevent="submitForm" class="form-grid">
      <!-- Row 1: Full Name and Category -->
      <div class="form-row-2">
        <div class="form-group">
          <label for="name">
            Full Name <span class="required">*</span>
          </label>
          <div class="input-with-icon">
            <span class="field-icon">👤</span>
            <input
              id="name"
              type="text"
              v-model.trim="name"
              placeholder="e.g. Alex Rivera"
              class="form-control with-icon"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label for="category">Category / Purpose</label>
          <div class="input-with-icon">
            <span class="field-icon">🏷️</span>
            <select id="category" v-model="category" class="form-control with-icon">
              <option value="Client">🏢 Client</option>
              <option value="Lead">💼 Lead</option>
              <option value="VIP">👑 VIP</option>
              <option value="Team Member">👥 Team Member</option>
              <option value="Engineering">💻 Engineering</option>
              <option value="Design">🎨 Design</option>
              <option value="Speaker">🎤 Speaker</option>
              <option value="Attendee">🎟️ Attendee</option>
              <option value="Vendor">📦 Vendor</option>
              <option value="General">🌐 General</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Row 2: Contact Number and Email -->
      <div class="form-row-2">
        <div class="form-group">
          <label for="contact">
            Phone / WhatsApp Number <span class="required">*</span>
          </label>
          <div class="input-with-icon">
            <span class="field-icon">📞</span>
            <input
              id="contact"
              type="tel"
              v-model="contact"
              placeholder="e.g. +1 415 555 0199 or 9876543210"
              class="form-control with-icon"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label for="email">
            Email Address <span class="optional">(Optional)</span>
          </label>
          <div class="input-with-icon">
            <span class="field-icon">✉️</span>
            <input
              id="email"
              type="email"
              v-model.trim="email"
              placeholder="e.g. alex.rivera@techflow.io"
              class="form-control with-icon"
            />
          </div>
        </div>
      </div>

      <!-- Address / Location -->
      <div class="form-group">
        <label for="address">
          Address / Physical Location <span class="required">*</span>
        </label>
        <div class="input-with-icon">
          <span class="field-icon">📍</span>
          <input
            id="address"
            type="text"
            v-model.trim="address"
            placeholder="e.g. 404 Silicon Ave, San Francisco, CA"
            class="form-control with-icon"
            required
          />
        </div>
      </div>

      <!-- Notes / Key Information -->
      <div class="form-group">
        <div class="label-row">
          <label for="notes">
            Notes, Role or Specific Instructions <span class="optional">(Optional)</span>
          </label>
          <span class="char-count">{{ notes.length }} / 300</span>
        </div>
        <textarea
          id="notes"
          v-model="notes"
          maxlength="300"
          placeholder="e.g. Lead Architect · Preferred contact time: Morning · Key deliverables: UI redesign..."
          rows="2"
          class="form-control textarea-control"
        ></textarea>
      </div>

      <!-- Drag & Drop Photo Uploader -->
      <div class="form-group">
        <label>
          Profile Avatar / Card Photo <span class="optional">(Optional)</span>
        </label>
        
        <div 
          class="upload-dropzone"
          :class="{ 'dropzone-active': isDragging, 'has-preview': !!imagePreview }"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
        >
          <input
            ref="fileInputRef"
            type="file"
            accept="image/png, image/jpeg, image/webp, image/gif"
            @change="handleFileChange"
            style="display: none;"
          />

          <!-- Preview Mode -->
          <div v-if="imagePreview" class="preview-container">
            <img :src="imagePreview" alt="Avatar preview" class="avatar-preview-img" />
            <div class="preview-meta">
              <span class="preview-status">✅ Photo Loaded</span>
              <button type="button" @click.stop="clearImage" class="btn-clear-photo">
                ✕ Remove Photo
              </button>
            </div>
          </div>

          <!-- Empty State Prompt -->
          <div v-else class="dropzone-prompt">
            <div class="upload-icon-circle">📷</div>
            <p class="upload-title"><strong>Click to browse</strong> or drag & drop a photo</p>
            <p class="upload-sub">Supports PNG, JPG, WEBP · Max 5MB (Auto-compressed)</p>
          </div>
        </div>
      </div>

      <!-- Submit Action Bar -->
      <div class="form-actions">
        <button
          type="button"
          @click="resetForm"
          class="btn-reset"
          :disabled="isSubmitting"
        >
          Reset
        </button>

        <button
          type="submit"
          class="btn-primary"
          :disabled="isSubmitting"
        >
          <span v-if="isSubmitting" class="spinner-small"></span>
          <span>{{ isSubmitting ? 'Saving Record...' : '🚀 Submit to Directory' }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { API_BASE_URL, isLocalPreview } from '../config'
import { addLocalDummyRecord, DIRECTORY_PRESETS } from '../dummyData'

const emit = defineEmits(['refresh'])

// Form fields
const name = ref('')
const address = ref('')
const contact = ref('')
const email = ref('')
const category = ref('Client')
const notes = ref('')
const imageFile = ref(null)
const imagePreview = ref('')
const isDragging = ref(false)
const fileInputRef = ref(null)

// UI status
const isSubmitting = ref(false)
const successMsg = ref('')
const errorMsg = ref('')

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

// Process selected file
const processImageFile = (file) => {
  if (!file) return
  if (!file.type.startsWith('image/')) {
    errorMsg.value = 'Please select a valid image file (JPG, PNG, or WEBP).'
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    errorMsg.value = 'Image size exceeds 5MB. Please choose a smaller photo.'
    return
  }

  errorMsg.value = ''
  imageFile.value = file

  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

const handleFileChange = (e) => {
  const file = e.target.files?.[0]
  if (file) processImageFile(file)
}

const handleDrop = (e) => {
  isDragging.value = false
  const file = e.dataTransfer.files?.[0]
  if (file) processImageFile(file)
}

const clearImage = () => {
  imageFile.value = null
  imagePreview.value = ''
  if (fileInputRef.value) fileInputRef.value.value = ''
}

// Autofill realistic sample data for instant testing
const fillDemoRecord = () => {
  const samples = [
    {
      name: "Sophia Chen",
      address: "72 Park Row, Suite 400, New York, NY",
      contact: "9123456780",
      email: "sophia.chen@vanguard.co",
      category: "Client",
      notes: "Enterprise Partner · Key Account Director · Contract renewal Q4",
      preview: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&auto=format&fit=crop&q=80"
    },
    {
      name: "Alex Rivera",
      address: "404 Silicon Ave, San Francisco, CA",
      contact: "9876543210",
      email: "alex.rivera@techflow.io",
      category: "Team Member",
      notes: "Lead Full-Stack Architect & 3D Interactive Graphics Engineer",
      preview: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80"
    },
    {
      name: "Marcus Vance",
      address: "15 King Street, Austin, TX",
      contact: "9012345678",
      email: "marcus.vance@apexlogistics.com",
      category: "Vendor",
      notes: "Logistics Coordinator & Specialized Fleet Logistics",
      preview: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80"
    },
    {
      name: "Dr. Jordan Blake",
      address: "88 University Ave, Cambridge, MA",
      contact: "9456781230",
      email: "j.blake@mit.edu",
      category: "VIP",
      notes: "Advisory Board Member · AI & High Performance Systems",
      preview: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop&q=80"
    }
  ]

  const randomSample = samples[Math.floor(Math.random() * samples.length)]
  name.value = randomSample.name
  address.value = randomSample.address
  contact.value = randomSample.contact
  email.value = randomSample.email
  category.value = randomSample.category
  notes.value = randomSample.notes
  imagePreview.value = randomSample.preview
  imageFile.value = null
  successMsg.value = `Filled sample record for ${randomSample.name}! Click 'Submit' to save it.`
  setTimeout(() => { successMsg.value = '' }, 4000)
}

const resetForm = () => {
  name.value = ''
  address.value = ''
  contact.value = ''
  email.value = ''
  category.value = 'Client'
  notes.value = ''
  clearImage()
  errorMsg.value = ''
  successMsg.value = ''
}

const submitForm = async () => {
  successMsg.value = ''
  errorMsg.value = ''

  if (!name.value || !address.value || !contact.value) {
    errorMsg.value = 'Please fill in all required fields (Name, Address, Phone).'
    return
  }

  isSubmitting.value = true

  try {
    // If on localhost without live backend, store locally
    if (isLocalPreview) {
      addLocalDummyRecord({
        name: name.value,
        address: address.value,
        contact: contact.value,
        email: email.value || null,
        category: category.value,
        notes: notes.value || null,
        image: imagePreview.value || ''
      })
      successMsg.value = `${name.value} was successfully added to your directory!`
      resetForm()
      emit('refresh')
      return
    }

    // Serverless API submission
    const formData = new FormData()
    formData.append('name', name.value)
    formData.append('address', address.value)
    formData.append('contact', contact.value)
    if (email.value) formData.append('email', email.value)
    formData.append('category', category.value)
    if (notes.value) formData.append('notes', notes.value)

    if (imageFile.value) {
      formData.append('image', imageFile.value)
    } else if (imagePreview.value && imagePreview.value.startsWith('http')) {
      // Pass sample image URL directly
      formData.append('image_url', imagePreview.value)
    }

    await axios.post(`${API_BASE_URL}/submit`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    successMsg.value = `${name.value} was successfully registered and saved!`
    resetForm()
    emit('refresh')
  } catch (err) {
    console.error('Submission failed:', err)
    // Fallback: If network or server error, save to local preview so user never loses work
    addLocalDummyRecord({
      name: name.value,
      address: address.value,
      contact: contact.value,
      email: email.value || null,
      category: category.value,
      notes: notes.value || null,
      image: imagePreview.value || ''
    })
    successMsg.value = `${name.value} saved to your browser session (Offline / Local Storage)!`
    resetForm()
    emit('refresh')
  } finally {
    isSubmitting.value = false
    setTimeout(() => {
      if (successMsg.value) successMsg.value = ''
    }, 5000)
  }
}
</script>
