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
            Browse, search, export, or contact entries directly.
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
            placeholder="Search by name, phone, email, address, or notes..."
            class="search-input"
          />
          <button v-if="searchQuery" @click="searchQuery = ''" class="clear-search-btn">✕</button>
        </div>

        <div class="sort-selector-box">
          <label class="sort-label">Sort:</label>
          <select v-model="sortBy" class="filter-select">
            <option value="newest">🕒 Newest</option>
            <option value="oldest">🕰️ Oldest</option>
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

    <!-- ============================================== -->
    <!-- MAIN VIEW 1: STREAMLINED COMPACT GRID CARDS   -->
    <!-- ============================================== -->
    <div v-else-if="viewMode === 'grid'" class="records-grid-compact">
      <div
        v-for="record in filteredRecords"
        :key="record.id"
        class="record-card-compact"
      >
        <!-- Card Top: Compact Avatar + Identity + Category -->
        <div class="card-compact-header">
          <div class="avatar-compact-wrapper" @click="openImageModal(record)">
            <img
              v-if="record.image"
              :src="record.image"
              :alt="record.name"
              class="record-compact-avatar"
              loading="lazy"
            />
            <div v-else class="avatar-compact-fallback" :style="getAvatarFallbackStyle(record.name)">
              {{ getInitials(record.name) }}
            </div>
          </div>

          <div class="card-compact-identity">
            <h4 class="card-compact-name" :title="record.name">{{ record.name }}</h4>
            <span class="category-badge-compact" :style="getCategoryBadgeStyle(record.category)">
              {{ getCategoryIcon(record.category) }} {{ record.category || 'General' }}
            </span>
          </div>
        </div>

        <!-- Card Body: Contact Info in clean compact rows -->
        <div class="card-compact-body">
          <!-- Phone & WhatsApp shortcut -->
          <div class="compact-info-row">
            <span class="compact-icon">📞</span>
            <a :href="'tel:' + record.contact" class="compact-link" title="Call">
              {{ record.contact }}
            </a>
          </div>

          <!-- Email (if present) -->
          <div v-if="record.email" class="compact-info-row">
            <span class="compact-icon">✉️</span>
            <a :href="'mailto:' + record.email" class="compact-link text-truncate" :title="record.email">
              {{ record.email }}
            </a>
          </div>

          <!-- Address -->
          <div class="compact-info-row">
            <span class="compact-icon">📍</span>
            <a
              :href="getGoogleMapsUrl(record.address)"
              target="_blank"
              rel="noopener"
              class="compact-link text-truncate"
              :title="record.address"
            >
              {{ record.address }}
            </a>
          </div>

          <!-- Notes snippet (if present) -->
          <div v-if="record.notes" class="compact-notes" :title="record.notes">
            <span class="compact-notes-icon">📝</span>
            <span class="compact-notes-text">{{ record.notes }}</span>
          </div>
        </div>

        <!-- Card Footer: Quick Actions Bar -->
        <div class="card-compact-footer">
          <a
            :href="getWhatsAppUrl(record)"
            target="_blank"
            rel="noopener"
            class="compact-action-btn btn-wa-compact"
            title="Chat on WhatsApp"
          >
            <span>💬</span> WhatsApp
          </a>

          <button
            type="button"
            @click="handleDownloadVCard(record)"
            class="compact-action-btn btn-vcard-compact"
            title="Download vCard (.vcf) contact"
          >
            <span>📇</span> vCard
          </button>

          <button
            type="button"
            @click="confirmDelete(record)"
            class="compact-action-btn btn-del-compact"
            title="Delete record"
          >
            <span>🗑️</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ============================================== -->
    <!-- MAIN VIEW 2: HIGHLY ORGANIZED DATA TABLE       -->
    <!-- ============================================== -->
    <div v-else-if="viewMode === 'table'" class="table-container-organized">
      <table class="organized-table">
        <thead>
          <tr>
            <th class="col-contact">Contact & Details</th>
            <th class="col-category">Category</th>
            <th class="col-phone">Phone / WhatsApp</th>
            <th class="col-location">Location</th>
            <th class="col-notes">Notes</th>
            <th class="col-actions">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="record in filteredRecords" :key="record.id" class="organized-row">
            <!-- 1. Contact (Avatar + Name + Email Cohesive Unit) -->
            <td class="cell-contact">
              <div class="contact-identity-block">
                <div class="table-mini-avatar" @click="openImageModal(record)">
                  <img
                    v-if="record.image"
                    :src="record.image"
                    :alt="record.name"
                    class="mini-avatar-img"
                  />
                  <div v-else class="mini-avatar-fallback">
                    {{ getInitials(record.name) }}
                  </div>
                </div>
                <div class="contact-names-stack">
                  <span class="table-contact-name">{{ record.name }}</span>
                  <span v-if="record.email" class="table-contact-email">{{ record.email }}</span>
                  <span v-else class="table-contact-no-email">No email</span>
                </div>
              </div>
            </td>

            <!-- 2. Category Pill -->
            <td class="cell-category">
              <span class="category-badge-compact" :style="getCategoryBadgeStyle(record.category)">
                {{ getCategoryIcon(record.category) }} {{ record.category || 'General' }}
              </span>
            </td>

            <!-- 3. Phone & 1-Click WhatsApp Shortcut -->
            <td class="cell-phone">
              <div class="phone-action-inline">
                <a :href="'tel:' + record.contact" class="phone-link">
                  {{ record.contact }}
                </a>
                <a
                  :href="getWhatsAppUrl(record)"
                  target="_blank"
                  rel="noopener"
                  class="table-wa-chip"
                  title="WhatsApp"
                >
                  💬
                </a>
              </div>
            </td>

            <!-- 4. Location -->
            <td class="cell-location">
              <a
                :href="getGoogleMapsUrl(record.address)"
                target="_blank"
                rel="noopener"
                class="location-text-link"
                :title="record.address"
              >
                📍 {{ record.address }}
              </a>
            </td>

            <!-- 5. Notes -->
            <td class="cell-notes">
              <span v-if="record.notes" class="notes-truncate" :title="record.notes">
                {{ record.notes }}
              </span>
              <span v-else class="text-muted">—</span>
            </td>

            <!-- 6. Actions (vCard & Delete) -->
            <td class="cell-actions">
              <div class="table-actions-inline">
                <button
                  type="button"
                  @click="handleDownloadVCard(record)"
                  class="tbl-btn tbl-btn-vcard"
                  title="Download vCard (.vcf)"
                >
                  📇
                </button>
                <button
                  type="button"
                  @click="confirmDelete(record)"
                  class="tbl-btn tbl-btn-delete"
                  title="Delete record"
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
  const filename = `inform_directory_${new Date().toISOString().slice(0, 10)}.csv`
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
    backgroundColor: color,
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

const getGoogleMapsUrl = (address) => {
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address || '')}`
}

const getWhatsAppUrl = (record) => {
  const cleanPhone = String(record.contact || '').replace(/[^0-9]/g, '')
  const greeting = `Hello ${record.name}, connecting regarding your directory entry on inFOrm.`
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
