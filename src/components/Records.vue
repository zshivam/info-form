<template>
  <div class="card">
    <!-- Header with Live Stats and Action Toolbar -->
    <div class="records-header-block">
      <div class="records-title-row">
        <div>
          <h2 class="card-title" style="margin-bottom: 0.25rem;">
            <span>👥</span> Directory Records
          </h2>
          <p class="section-desc">Manage, search, contact, and export directory entries.</p>
        </div>
        <div class="header-action-group">
          <button @click="exportCSV" class="btn-action-outline" :disabled="records.length === 0" title="Export entries to spreadsheet">
            <span>📥</span> Export CSV
          </button>
          <button @click="loadRecords" class="btn-action-outline" :disabled="isLoading" title="Refresh list from server">
            <span>{{ isLoading ? '⏳' : '🔄' }}</span> Refresh
          </button>
        </div>
      </div>

      <!-- Quick Stats Dashboard -->
      <div v-if="records.length > 0" class="stats-bar">
        <div class="stat-pill stat-total">
          <span class="stat-label">Total Entries</span>
          <span class="stat-value">{{ records.length }}</span>
        </div>
        <div
          v-for="(count, cat) in categoryCounts"
          :key="cat"
          class="stat-pill"
          :class="{ 'stat-pill-active': selectedCategory === cat }"
          @click="selectCategory(cat)"
        >
          <span class="stat-label">{{ cat }}</span>
          <span class="stat-value">{{ count }}</span>
        </div>
      </div>

      <!-- Search, Category Filter, and Sorting Controls -->
      <div class="filter-controls-row">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input
            type="text"
            v-model.trim="searchQuery"
            placeholder="Search by name, phone, email, address, or notes..."
            class="search-input"
          />
          <button v-if="searchQuery" @click="searchQuery = ''" class="clear-search-btn">✕</button>
        </div>

        <div class="filter-dropdowns">
          <select v-model="selectedCategory" class="filter-select">
            <option value="All">All Categories ({{ records.length }})</option>
            <option v-for="cat in availableCategories" :key="cat" :value="cat">
              {{ cat }}
            </option>
          </select>

          <select v-model="sortBy" class="filter-select">
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="name_asc">Name (A → Z)</option>
            <option value="name_desc">Name (Z → A)</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="errorMsg" class="alert alert-danger" style="margin-top: 1.5rem;">
      <p>{{ errorMsg }}</p>
      <button @click="loadRecords" class="btn-refresh" style="margin-top: 0.5rem;">Try Again</button>
    </div>

    <!-- Loading State -->
    <div v-else-if="isLoading && records.length === 0" class="empty-state">
      <div class="spinner-large"></div>
      <p style="margin-top: 1rem;">Loading directory records...</p>
    </div>

    <!-- Empty Database State -->
    <div v-else-if="records.length === 0" class="empty-state">
      <div class="empty-state-icon">📭</div>
      <h3>Directory is Empty</h3>
      <p>Submit your first entry using the form above to get started.</p>
    </div>

    <!-- Filter Zero-Results State -->
    <div v-else-if="filteredRecords.length === 0" class="empty-state">
      <div class="empty-state-icon">🔎</div>
      <h3>No Matches Found</h3>
      <p>No records match your search criteria "{{ searchQuery }}".</p>
      <button @click="resetFilters" class="btn-secondary" style="margin-top: 0.75rem;">
        Clear Filters
      </button>
    </div>

    <!-- Records Grid -->
    <div v-else class="records-grid" style="margin-top: 1.5rem;">
      <div v-for="item in filteredRecords" :key="item.id" class="record-card">
        <!-- Photo with Lightbox click -->
        <div class="record-image-wrapper" @click="openLightbox(item)">
          <img
            v-if="item.image"
            :src="getImageUrl(item.image)"
            :alt="item.name"
            class="record-image"
            @error="handleImageError($event)"
            loading="lazy"
          />
          <div v-else class="record-image-placeholder">No Photo</div>
          <span class="category-tag" :class="'cat-' + sanitizeClass(item.category || 'General')">
            {{ item.category || 'General' }}
          </span>
          <div class="image-zoom-overlay">
            <span>🔍 View Photo</span>
          </div>
        </div>

        <!-- Details Body -->
        <div class="record-body">
          <div class="record-name-row">
            <h3 class="record-name">{{ item.name }}</h3>
            <span class="record-id-badge">#{{ item.id }}</span>
          </div>

          <div class="record-details-list">
            <!-- Contact -->
            <div class="record-info-row">
              <span class="info-icon">📞</span>
              <a :href="'tel:' + item.contact" class="info-link" title="Click to call">
                {{ item.contact }}
              </a>
            </div>

            <!-- Email -->
            <div v-if="item.email" class="record-info-row">
              <span class="info-icon">✉️</span>
              <a :href="'mailto:' + item.email" class="info-link" title="Click to email">
                {{ item.email }}
              </a>
            </div>

            <!-- Address -->
            <div class="record-info-row">
              <span class="info-icon">📍</span>
              <a
                :href="'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(item.address)"
                target="_blank"
                rel="noopener"
                class="info-link"
                title="View location in Google Maps"
              >
                {{ item.address }}
              </a>
            </div>

            <!-- Notes -->
            <div v-if="item.notes" class="record-notes-box">
              <p class="notes-text">"{{ item.notes }}"</p>
            </div>
          </div>

          <!-- Quick Action Buttons -->
          <div class="card-quick-actions">
            <a
              :href="'https://wa.me/' + cleanPhone(item.contact)"
              target="_blank"
              rel="noopener"
              class="quick-btn btn-wa"
              title="Message on WhatsApp"
            >
              💬 WhatsApp
            </a>
            <a
              :href="'tel:' + item.contact"
              class="quick-btn btn-call"
              title="Call Phone Number"
            >
              📞 Call
            </a>
            <button
              @click="confirmDelete(item)"
              class="quick-btn btn-del"
              title="Delete record"
              :disabled="deletingId === item.id"
            >
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Image Lightbox Modal -->
    <div v-if="lightboxItem" class="modal-backdrop" @click.self="closeLightbox">
      <div class="modal-card">
        <div class="modal-header">
          <h3>{{ lightboxItem.name }} ({{ lightboxItem.category || 'General' }})</h3>
          <button class="modal-close-btn" @click="closeLightbox">✕</button>
        </div>
        <div class="modal-image-container">
          <img :src="getImageUrl(lightboxItem.image)" :alt="lightboxItem.name" class="modal-full-img" />
        </div>
        <div class="modal-footer">
          <p>📍 {{ lightboxItem.address }} | 📞 {{ lightboxItem.contact }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, computed, onMounted } from 'vue'
import { API_BASE_URL, getImageUrl } from '../config'
import { getLocalDummyRecords, deleteLocalDummyRecord } from '../dummyData'

const records = ref([])
const isLoading = ref(false)
const errorMsg = ref("")
const deletingId = ref(null)

// Filtering & Search
const searchQuery = ref("")
const selectedCategory = ref("All")
const sortBy = ref("newest")

// Lightbox
const lightboxItem = ref(null)

const handleImageError = (e) => {
  e.target.style.display = 'none'
  if (e.target.parentElement) {
    const placeholder = document.createElement('div')
    placeholder.className = 'record-image-placeholder'
    placeholder.innerText = 'Image not available'
    e.target.parentElement.appendChild(placeholder)
  }
}

function sanitizeClass(str) {
  return String(str).toLowerCase().replace(/[^a-z0-9]/g, '-')
}

function cleanPhone(phone) {
  return String(phone || '').replace(/[^0-9]/g, '')
}

function selectCategory(cat) {
  selectedCategory.value = selectedCategory.value === cat ? 'All' : cat
}

function resetFilters() {
  searchQuery.value = ""
  selectedCategory.value = "All"
  sortBy.value = "newest"
}

function openLightbox(item) {
  lightboxItem.value = item
}

function closeLightbox() {
  lightboxItem.value = null
}

// Compute categories and stats
const availableCategories = computed(() => {
  const set = new Set()
  records.value.forEach(r => {
    if (r.category) set.add(r.category)
  })
  return Array.from(set)
})

const categoryCounts = computed(() => {
  const counts = {}
  records.value.forEach(r => {
    const cat = r.category || 'General'
    counts[cat] = (counts[cat] || 0) + 1
  })
  return counts
})

// Filtered and Sorted Records
const filteredRecords = computed(() => {
  let list = [...records.value]

  // Category filter
  if (selectedCategory.value && selectedCategory.value !== 'All') {
    list = list.filter(item => (item.category || 'General') === selectedCategory.value)
  }

  // Search query filter
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(item => {
      const nameMatch = item.name?.toLowerCase().includes(q)
      const addressMatch = item.address?.toLowerCase().includes(q)
      const contactMatch = String(item.contact || '').includes(q)
      const emailMatch = item.email?.toLowerCase().includes(q)
      const notesMatch = item.notes?.toLowerCase().includes(q)
      const categoryMatch = item.category?.toLowerCase().includes(q)
      return nameMatch || addressMatch || contactMatch || emailMatch || notesMatch || categoryMatch
    })
  }

  // Sorting
  if (sortBy.value === 'newest') {
    list.sort((a, b) => (b.id || 0) - (a.id || 0))
  } else if (sortBy.value === 'oldest') {
    list.sort((a, b) => (a.id || 0) - (b.id || 0))
  } else if (sortBy.value === 'name_asc') {
    list.sort((a, b) => (a.name || '').localeCompare(b.name || ''))
  } else if (sortBy.value === 'name_desc') {
    list.sort((a, b) => (b.name || '').localeCompare(a.name || ''))
  }

  return list
})

const loadRecords = async () => {
  isLoading.value = true
  errorMsg.value = ""
  try {
    const res = await axios.get(`${API_BASE_URL}/records/`)
    const data = Array.isArray(res.data) ? res.data : []
    if (data.length > 0) {
      records.value = data
    } else {
      // Production database is clean and empty!
      // But if running locally on localhost, load rich dummy data for demo
      const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      records.value = isLocalhost ? getLocalDummyRecords() : []
    }
  } catch (error) {
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    if (isLocalhost) {
      records.value = getLocalDummyRecords()
    } else {
      console.error('Error loading records:', error)
      errorMsg.value = `Unable to connect to records service (${error.message}). Please check backend connectivity.`
    }
  } finally {
    isLoading.value = false
  }
}

const confirmDelete = async (item) => {
  if (!confirm(`Are you sure you want to delete the record for "${item.name}"?`)) {
    return
  }

  deletingId.value = item.id
  try {
    await axios.delete(`${API_BASE_URL}/records/${item.id}/`)
    records.value = records.value.filter(r => r.id !== item.id)
  } catch (error) {
    if (String(item.id).startsWith('demo-')) {
      records.value = deleteLocalDummyRecord(item.id)
    } else {
      console.error('Error deleting record:', error)
      alert(`Failed to delete record: ${error.response?.data?.detail || error.message}`)
    }
  } finally {
    deletingId.value = null
  }
}


// Export records to CSV
const exportCSV = () => {
  if (filteredRecords.value.length === 0) {
    alert("No records to export.")
    return
  }

  const headers = ["ID", "Name", "Category", "Contact", "Email", "Address", "Notes", "Photo Filename"]
  const rows = filteredRecords.value.map(r => [
    r.id ?? '',
    `"${(r.name || '').replace(/"/g, '""')}"`,
    `"${(r.category || 'General').replace(/"/g, '""')}"`,
    `"${r.contact ?? ''}"`,
    `"${(r.email || '').replace(/"/g, '""')}"`,
    `"${(r.address || '').replace(/"/g, '""')}"`,
    `"${(r.notes || '').replace(/"/g, '""')}"`,
    `"${r.image ?? ''}"`
  ])

  const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows.map(e => e.join(','))].join('\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement("a")
  link.setAttribute("href", encodedUri)
  const dateStr = new Date().toISOString().slice(0, 10)
  link.setAttribute("download", `directory_records_${dateStr}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

onMounted(() => {
  loadRecords()
})

defineExpose({
  loadRecords,
  loadData: loadRecords
})
</script>
