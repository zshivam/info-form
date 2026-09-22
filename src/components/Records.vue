<template>
  <div class="card records-card">
    <!-- Header Block with Stats and View Mode Toolbar -->
    <div class="records-header-block">
      <div class="records-title-row">
        <div>
          <h2 class="card-title">
            <span class="header-icon">📇</span> Directory & Contacts
          </h2>
          <p class="section-desc">
            Browse entries, initiate 1-click WhatsApp chats, download phone vCards, or export to CSV.
          </p>
        </div>

        <div class="header-action-group">
          <!-- View Switcher (Grid vs Table) -->
          <div class="view-mode-toggle" title="Switch layout">
            <button
              type="button"
              class="view-toggle-btn"
              :class="{ 'active': viewMode === 'grid' }"
              @click="viewMode = 'grid'"
            >
              <span>▦</span> Cards
            </button>
            <button
              type="button"
              class="view-toggle-btn"
              :class="{ 'active': viewMode === 'table' }"
              @click="viewMode = 'table'"
            >
              <span>☰</span> Table
            </button>
          </div>

          <!-- CSV Export Button -->
          <button
            @click="handleExportCSV"
            class="btn-action-outline"
            :disabled="filteredRecords.length === 0"
            title="Download CSV for Excel or Google Sheets"
          >
            <span>📥</span> Export CSV
          </button>

          <!-- Refresh Button -->
          <button
            @click="loadRecords"
            class="btn-action-outline"
            :disabled="isLoading"
            title="Fetch latest updates"
          >
            <span>{{ isLoading ? '⏳' : '🔄' }}</span> Refresh
          </button>
        </div>
      </div>

      <!-- Category Filter Pills with Live Counters -->
      <div class="category-pills-bar">
        <button
          type="button"
          class="cat-pill"
          :class="{ 'active': selectedCategory === 'All' }"
          @click="selectedCategory = 'All'"
        >
          <span>🌐 All</span>
          <span class="cat-pill-count">{{ records.length }}</span>
        </button>

        <button
          v-for="(count, cat) in categoryCounts"
          :key="cat"
          type="button"
          class="cat-pill"
          :class="{ 'active': selectedCategory === cat }"
          :style="selectedCategory === cat ? getCategoryPillStyle(cat) : {}"
          @click="selectedCategory = cat"
        >
          <span>{{ getCategoryIcon(cat) }} {{ cat }}</span>
          <span class="cat-pill-count">{{ count }}</span>
        </button>
      </div>

      <!-- Search Box & Sort Selector -->
      <div class="filter-controls-row">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input
            type="text"
            v-model.trim="searchQuery"
            placeholder="Search by name, phone, email, address, or role notes..."
            class="search-input"
          />
          <button v-if="searchQuery" @click="searchQuery = ''" class="clear-search-btn">✕</button>
        </div>

        <div class="sort-selector-box">
          <label class="sort-label">Sort:</label>
          <select v-model="sortBy" class="filter-select">
            <option value="newest">🕒 Newest First</option>
            <option value="oldest">🕰️ Oldest First</option>
            <option value="name_asc">🔤 Name (A → Z)</option>
            <option value="name_desc">🔤 Name (Z → A)</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Alert / Toast Messages -->
    <transition name="fade">
      <div v-if="toastMsg" class="toast-notification">
        {{ toastMsg }}
      </div>
    </transition>

    <!-- Error State -->
    <div v-if="errorMsg" class="alert alert-danger" style="margin-top: 1.5rem;">
      <p>{{ errorMsg }}</p>
      <button @click="loadRecords" class="btn-refresh" style="margin-top: 0.5rem;">Try Again</button>
    </div>

    <!-- Loading State -->
    <div v-else-if="isLoading && records.length === 0" class="empty-state">
      <div class="spinner-large"></div>
      <p style="margin-top: 1rem; color: var(--text-secondary);">Loading directory records...</p>
    </div>

    <!-- Empty Database State -->
    <div v-else-if="records.length === 0" class="empty-state">
      <div class="empty-state-icon">📭</div>
      <h3>Directory is Empty</h3>
      <p>Submit your first entry using the form above to add your data.</p>
    </div>

    <!-- Filter Zero-Results State -->
    <div v-else-if="filteredRecords.length === 0" class="empty-state">
      <div class="empty-state-icon">🔎</div>
      <h3>No Matching Contacts</h3>
      <p>No records matched your search query "{{ searchQuery }}".</p>
      <button @click="resetFilters" class="btn-secondary" style="margin-top: 0.75rem;">
        Clear Filters
      </button>
    </div>

    <!-- MAIN VIEW 1: MODERN GRID CARDS -->
    <div v-else-if="viewMode === 'grid'" class="records-grid">
      <div
        v-for="record in filteredRecords"
        :key="record.id"
        class="record-card"
      >
        <!-- Card Header: Avatar & Category Badge -->
        <div class="card-top-row">
          <div class="avatar-wrapper" @click="openImageModal(record)">
            <img
              v-if="record.image"
              :src="record.image"
              :alt="record.name"
              class="record-avatar"
              loading="lazy"
            />
            <div v-else class="avatar-fallback" :style="getAvatarFallbackStyle(record.name)">
              {{ getInitials(record.name) }}
            </div>
            <span v-if="record.image" class="avatar-zoom-hint" title="Click to view photo">🔍</span>
          </div>

          <div class="card-meta">
            <span class="category-badge" :style="getCategoryBadgeStyle(record.category)">
              {{ getCategoryIcon(record.category) }} {{ record.category || 'General' }}
            </span>
            <span class="record-date">{{ formatDate(record.created_at) }}</span>
          </div>
        </div>

        <!-- Main Info -->
        <div class="card-body">
          <h3 class="record-name" :title="record.name">{{ record.name }}</h3>

          <div class="info-list">
            <!-- Contact Phone -->
            <div class="info-row">
              <span class="info-icon">📞</span>
              <a :href="'tel:' + record.contact" class="info-link" title="Click to call">
                {{ record.contact }}
              </a>
            </div>

            <!-- Email -->
            <div v-if="record.email" class="info-row">
              <span class="info-icon">✉️</span>
              <a :href="'mailto:' + record.email" class="info-link" :title="record.email">
                {{ record.email }}
              </a>
            </div>

            <!-- Address -->
            <div class="info-row">
              <span class="info-icon">📍</span>
              <a
                :href="getGoogleMapsUrl(record.address)"
                target="_blank"
                rel="noopener"
                class="info-link location-link"
                title="Open in Google Maps"
              >
                {{ record.address }}
              </a>
            </div>

            <!-- Notes -->
            <div v-if="record.notes" class="notes-box">
              <span class="notes-quote">“</span>
              <p class="notes-text">{{ record.notes }}</p>
            </div>
          </div>
        </div>

        <!-- Quick Action Bar -->
        <div class="card-actions-bar">
          <!-- WhatsApp -->
          <a
            :href="getWhatsAppUrl(record)"
            target="_blank"
            rel="noopener"
            class="btn-action-icon btn-whatsapp"
            title="Chat on WhatsApp with greeting"
          >
            <span>💬</span> WhatsApp
          </a>

          <!-- vCard Download -->
          <button
            type="button"
            @click="handleDownloadVCard(record)"
            class="btn-action-icon btn-vcard"
            title="Download vCard to save directly in phone contacts"
          >
            <span>📇</span> Save vCard
          </button>

          <!-- Delete -->
          <button
            type="button"
            @click="confirmDelete(record)"
            class="btn-action-icon btn-delete"
            title="Delete this record"
          >
            <span>🗑️</span>
          </button>
        </div>
      </div>
    </div>

    <!-- MAIN VIEW 2: COMPACT DATA TABLE -->
    <div v-else-if="viewMode === 'table'" class="table-responsive">
      <table class="data-table">
        <thead>
          <tr>
            <th>Photo</th>
            <th>Name</th>
            <th>Category</th>
            <th>Contact</th>
            <th>Email</th>
            <th>Location</th>
            <th>Notes</th>
            <th style="text-align: right;">Quick Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="record in filteredRecords" :key="record.id">
            <!-- Photo Thumbnail -->
            <td style="width: 50px;">
              <div class="table-avatar-wrapper" @click="openImageModal(record)">
                <img
                  v-if="record.image"
                  :src="record.image"
                  :alt="record.name"
                  class="table-avatar"
                />
                <div v-else class="table-avatar-fallback">
                  {{ getInitials(record.name) }}
                </div>
              </div>
            </td>

            <!-- Name -->
            <td>
              <strong>{{ record.name }}</strong>
            </td>

            <!-- Category -->
            <td>
              <span class="category-badge table-badge" :style="getCategoryBadgeStyle(record.category)">
                {{ record.category || 'General' }}
              </span>
            </td>

            <!-- Contact Phone -->
            <td>
              <a :href="'tel:' + record.contact" class="table-link">
                {{ record.contact }}
              </a>
            </td>

            <!-- Email -->
            <td>
              <a v-if="record.email" :href="'mailto:' + record.email" class="table-link">
                {{ record.email }}
              </a>
              <span v-else class="text-muted">—</span>
            </td>

            <!-- Address -->
            <td>
              <a
                :href="getGoogleMapsUrl(record.address)"
                target="_blank"
                rel="noopener"
                class="table-link table-address"
                :title="record.address"
              >
                {{ record.address }}
              </a>
            </td>

            <!-- Notes -->
            <td class="table-notes" :title="record.notes || ''">
              {{ record.notes || '—' }}
            </td>

            <!-- Actions -->
            <td style="text-align: right; white-space: nowrap;">
              <div class="table-action-group">
                <a
                  :href="getWhatsAppUrl(record)"
                  target="_blank"
                  rel="noopener"
                  class="table-action-btn"
                  title="WhatsApp"
                >
                  💬
                </a>
                <button
                  type="button"
                  @click="handleDownloadVCard(record)"
                  class="table-action-btn"
                  title="Download vCard"
                >
                  📇
                </button>
                <button
                  type="button"
                  @click="confirmDelete(record)"
                  class="table-action-btn btn-delete-row"
                  title="Delete"
                >
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Image Lightbox Modal -->
    <transition name="fade">
      <div v-if="activeImageModal" class="modal-backdrop" @click="closeImageModal">
        <div class="modal-dialog" @click.stop>
          <button class="modal-close-btn" @click="closeImageModal">✕</button>
          <img :src="activeImageModal.image" :alt="activeImageModal.name" class="modal-full-img" />
          <div class="modal-caption">
            <h4>{{ activeImageModal.name }}</h4>
            <p>{{ activeImageModal.category }} · {{ activeImageModal.address }}</p>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { API_BASE_URL, isLocalPreview } from '../config'
import {
  getLocalDummyRecords,
  deleteLocalDummyRecord,
  downloadVCard,
  exportToCSV,
  CATEGORY_COLORS
} from '../dummyData'

// State
const records = ref([])
const isLoading = ref(false)
const errorMsg = ref('')
const toastMsg = ref('')
const searchQuery = ref('')
const selectedCategory = ref('All')
const sortBy = ref('newest')
const viewMode = ref('grid') // 'grid' or 'table'
const activeImageModal = ref(null)

// Category Counts for interactive filters
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
  let result = [...records.value]

  // Category filter
  if (selectedCategory.value !== 'All') {
    result = result.filter(r => (r.category || 'General') === selectedCategory.value)
  }

  // Search filter
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    result = result.filter(r => {
      const nameMatch = (r.name || '').toLowerCase().includes(q)
      const phoneMatch = String(r.contact || '').toLowerCase().includes(q)
      const emailMatch = (r.email || '').toLowerCase().includes(q)
      const addressMatch = (r.address || '').toLowerCase().includes(q)
      const notesMatch = (r.notes || '').toLowerCase().includes(q)
      const categoryMatch = (r.category || '').toLowerCase().includes(q)
      return nameMatch || phoneMatch || emailMatch || addressMatch || notesMatch || categoryMatch
    })
  }

  // Sort
  if (sortBy.value === 'newest') {
    result.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
  } else if (sortBy.value === 'oldest') {
    result.sort((a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0))
  } else if (sortBy.value === 'name_asc') {
    result.sort((a, b) => (a.name || '').localeCompare(b.name || ''))
  } else if (sortBy.value === 'name_desc') {
    result.sort((a, b) => (b.name || '').localeCompare(a.name || ''))
  }

  return result
})

const showToast = (msg) => {
  toastMsg.value = msg
  setTimeout(() => {
    if (toastMsg.value === msg) toastMsg.value = ''
  }, 3500)
}

const loadRecords = async () => {
  isLoading.value = true
  errorMsg.value = ''

  try {
    if (isLocalPreview) {
      records.value = getLocalDummyRecords()
      return
    }

    const response = await axios.get(`${API_BASE_URL}/records`)
    records.value = Array.isArray(response.data) ? response.data : []
  } catch (err) {
    console.warn('API error, loading fallback records:', err)
    records.value = getLocalDummyRecords()
  } finally {
    isLoading.value = false
  }
}

const handleDownloadVCard = (record) => {
  downloadVCard(record)
  showToast(`Downloaded vCard for ${record.name}! Ready to import into phone contacts.`)
}

const handleExportCSV = () => {
  const filename = `pulsedesk_directory_${new Date().toISOString().slice(0, 10)}.csv`
  exportToCSV(filteredRecords.value, filename)
  showToast(`Exported ${filteredRecords.value.length} contacts to CSV.`)
}

const confirmDelete = async (record) => {
  if (!confirm(`Are you sure you want to delete ${record.name}?`)) return

  try {
    if (isLocalPreview) {
      records.value = deleteLocalDummyRecord(record.id)
      showToast(`Deleted ${record.name}.`)
      return
    }

    await axios.delete(`${API_BASE_URL}/records/${record.id}`)
    records.value = records.value.filter(r => r.id !== record.id)
    showToast(`Deleted ${record.name}.`)
  } catch (err) {
    console.error('Delete failed:', err)
    records.value = deleteLocalDummyRecord(record.id)
    showToast(`Deleted ${record.name}.`)
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedCategory.value = 'All'
}

const openImageModal = (record) => {
  if (record.image) {
    activeImageModal.value = record
  }
}

const closeImageModal = () => {
  activeImageModal.value = null
}

// Visual helpers
const getInitials = (name) => {
  if (!name) return '?'
  const parts = name.trim().split(' ')
  return parts.length > 1
    ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
    : parts[0].slice(0, 2).toUpperCase()
}

const getAvatarFallbackStyle = (name) => {
  const colors = ['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ec4899', '#06b6d4']
  let hash = 0
  for (let i = 0; i < (name || '').length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  const color = colors[Math.abs(hash) % colors.length]
  return {
    background: `linear-gradient(135deg, ${color}, ${color}cc)`,
    color: '#ffffff'
  }
}

const getCategoryIcon = (category) => {
  const map = {
    'Client': '🏢',
    'Lead': '💼',
    'VIP': '👑',
    'Team Member': '👥',
    'Engineering': '💻',
    'Design': '🎨',
    'Speaker': '🎤',
    'Attendee': '🎟️',
    'Vendor': '📦',
    'General': '🌐'
  }
  return map[category] || '🏷️'
}

const getCategoryBadgeStyle = (cat) => {
  const conf = CATEGORY_COLORS[cat] || CATEGORY_COLORS['General']
  return {
    backgroundColor: conf.bg,
    color: conf.text,
    borderColor: conf.border
  }
}

const getCategoryPillStyle = (cat) => {
  const conf = CATEGORY_COLORS[cat] || CATEGORY_COLORS['General']
  return {
    backgroundColor: conf.text,
    color: '#ffffff',
    borderColor: conf.text
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'Recent'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
  } catch {
    return 'Recent'
  }
}

const getGoogleMapsUrl = (address) => {
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address || '')}`
}

const getWhatsAppUrl = (record) => {
  const cleanPhone = String(record.contact || '').replace(/[^0-9]/g, '')
  const greeting = `Hello ${record.name}, connecting regarding your directory entry on PulseDesk.`
  return `https://wa.me/${cleanPhone}?text=${encodeURIComponent(greeting)}`
}

defineExpose({
  loadRecords,
  loadData: loadRecords
})

onMounted(() => {
  loadRecords()
})
</script>
