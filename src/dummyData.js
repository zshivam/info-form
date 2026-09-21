// Realistic dummy records for localhost preview
const INITIAL_DUMMY_RECORDS = [
  {
    id: "demo-1",
    name: "Alex Rivera",
    address: "404 Silicon Ave, San Francisco, CA",
    contact: 9876543210,
    email: "alex.rivera@techflow.io",
    category: "Team Member",
    notes: "Lead Full-Stack Architect & UI Designer",
    image: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80",
    created_at: "2026-09-20T10:00:00Z"
  },
  {
    id: "demo-2",
    name: "Sophia Chen",
    address: "72 Park Row, New York, NY",
    contact: 9123456780,
    email: "sophia.chen@vanguard.co",
    category: "Client",
    notes: "Enterprise Partner - Key Account Director",
    image: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&auto=format&fit=crop&q=80",
    created_at: "2026-09-19T14:30:00Z"
  },
  {
    id: "demo-3",
    name: "Marcus Vance",
    address: "15 King Street, Austin, TX",
    contact: 9012345678,
    email: "marcus.vance@apexlogistics.com",
    category: "Vendor",
    notes: "Logistics Coordinator & Equipment Specialist",
    image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80",
    created_at: "2026-09-18T09:15:00Z"
  }
]

const STORAGE_KEY = 'info_form_local_dummy_records'

export function getLocalDummyRecords() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const parsed = JSON.parse(saved)
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed
      }
    }
  } catch (e) {
    console.warn("Could not read localStorage:", e)
  }
  return [...INITIAL_DUMMY_RECORDS]
}

export function saveLocalDummyRecords(records) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(records))
  } catch (e) {
    console.warn("Could not save to localStorage:", e)
  }
}

export function addLocalDummyRecord(entry) {
  const current = getLocalDummyRecords()
  const newRecord = {
    id: `demo-${Date.now().toString().slice(-6)}`,
    ...entry,
    created_at: new Date().toISOString()
  }
  const updated = [newRecord, ...current]
  saveLocalDummyRecords(updated)
  return newRecord
}

export function deleteLocalDummyRecord(id) {
  const current = getLocalDummyRecords()
  const updated = current.filter(item => String(item.id) !== String(id))
  saveLocalDummyRecords(updated)
  return updated
}
