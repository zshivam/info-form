// Purpose Presets and Category Configurations
export const DIRECTORY_PRESETS = [
  {
    id: "crm",
    name: "Client CRM",
    icon: "🏢",
    description: "Manage client leads, enterprise accounts, and sales pipelines",
    defaultCategory: "Client",
    categories: ["Client", "Lead", "VIP", "Prospect", "Partner"],
    sampleRecords: [
      {
        name: "Sophia Chen",
        address: "72 Park Row, Suite 400, New York, NY",
        contact: 9123456780,
        email: "sophia.chen@vanguard.co",
        category: "Client",
        notes: "Enterprise Partner · Key Account Director · Contract renewal Q4",
        image: "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&auto=format&fit=crop&q=80"
      },
      {
        name: "David Sterling",
        address: "1200 Market St, Philadelphia, PA",
        contact: 9812345670,
        email: "david@sterlingventures.io",
        category: "VIP",
        notes: "Series-A Investor · Interested in API automation suite",
        image: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop&q=80"
      }
    ]
  },
  {
    id: "team",
    name: "Team Directory",
    icon: "👥",
    description: "Visual staff rolodex with roles, skills, and contact shortcuts",
    defaultCategory: "Team Member",
    categories: ["Team Member", "Engineering", "Design", "Management", "Operations"],
    sampleRecords: [
      {
        name: "Alex Rivera",
        address: "404 Silicon Ave, San Francisco, CA",
        contact: 9876543210,
        email: "alex.rivera@techflow.io",
        category: "Team Member",
        notes: "Lead Full-Stack Architect & Three.js Graphics Engineer",
        image: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80"
      },
      {
        name: "Elena Rostova",
        address: "88 Broadway, Seattle, WA",
        contact: 9345678901,
        email: "elena.r@techflow.io",
        category: "Design",
        notes: "Head of Product Design & Brand Experience",
        image: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&auto=format&fit=crop&q=80"
      }
    ]
  },
  {
    id: "events",
    name: "Event Guests",
    icon: "🎟️",
    description: "Attendee check-in, guest badges, and registration records",
    defaultCategory: "Attendee",
    categories: ["Attendee", "Speaker", "VIP", "Organizer", "Sponsor"],
    sampleRecords: [
      {
        name: "Liam O'Connor",
        address: "Austin Convention Center, TX",
        contact: 9789012345,
        email: "liam@fintechsummit.org",
        category: "Speaker",
        notes: "Keynote: 'The Future of Serverless Web Platforms' (Hall A - 11:00 AM)",
        image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&auto=format&fit=crop&q=80"
      }
    ]
  },
  {
    id: "vendors",
    name: "Vendors & Logistics",
    icon: "📦",
    description: "Suppliers, contractors, logistics, and partner contacts",
    defaultCategory: "Vendor",
    categories: ["Vendor", "Supplier", "Contractor", "Logistics", "Maintenance"],
    sampleRecords: [
      {
        name: "Marcus Vance",
        address: "15 King Street, Austin, TX",
        contact: 9012345678,
        email: "marcus.vance@apexlogistics.com",
        category: "Vendor",
        notes: "Fleet Manager · Fast Freight & Warehouse Coordination",
        image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80"
      }
    ]
  }
]

// Default category color mappings for consistent visual cues
export const CATEGORY_COLORS = {
  "Client": { bg: "rgba(59, 130, 246, 0.12)", text: "#2563eb", border: "rgba(59, 130, 246, 0.3)" },
  "Lead": { bg: "rgba(245, 158, 11, 0.12)", text: "#d97706", border: "rgba(245, 158, 11, 0.3)" },
  "VIP": { bg: "rgba(168, 85, 247, 0.12)", text: "#9333ea", border: "rgba(168, 85, 247, 0.3)" },
  "Team Member": { bg: "rgba(16, 185, 129, 0.12)", text: "#059669", border: "rgba(16, 185, 129, 0.3)" },
  "Engineering": { bg: "rgba(14, 165, 233, 0.12)", text: "#0284c7", border: "rgba(14, 165, 233, 0.3)" },
  "Design": { bg: "rgba(236, 72, 153, 0.12)", text: "#db2777", border: "rgba(236, 72, 153, 0.3)" },
  "Speaker": { bg: "rgba(249, 115, 22, 0.12)", text: "#ea580c", border: "rgba(249, 115, 22, 0.3)" },
  "Attendee": { bg: "rgba(99, 102, 241, 0.12)", text: "#4f46e5", border: "rgba(99, 102, 241, 0.3)" },
  "Vendor": { bg: "rgba(100, 116, 139, 0.12)", text: "#475569", border: "rgba(100, 116, 139, 0.3)" },
  "General": { bg: "rgba(107, 114, 128, 0.12)", text: "#4b5563", border: "rgba(107, 114, 128, 0.3)" }
}

// Generate vCard (.vcf) formatted string for downloading direct to phone/contacts
export function generateVCard(record) {
  const nameParts = (record.name || "Contact").split(" ")
  const lastName = nameParts.length > 1 ? nameParts.slice(1).join(" ") : ""
  const firstName = nameParts[0] || ""

  return [
    "BEGIN:VCARD",
    "VERSION:3.0",
    `N:${lastName};${firstName};;;`,
    `FN:${record.name || "Contact"}`,
    record.category ? `ORG:${record.category}` : "",
    record.contact ? `TEL;TYPE=CELL:${record.contact}` : "",
    record.email ? `EMAIL;TYPE=INTERNET:${record.email}` : "",
    record.address ? `ADR;TYPE=WORK:;;${record.address};;;;` : "",
    record.notes ? `NOTE:${record.notes.replace(/\n/g, " ")}` : "",
    "END:VCARD"
  ].filter(Boolean).join("\r\n")
}

// Trigger browser download of vCard file
export function downloadVCard(record) {
  const vcfContent = generateVCard(record)
  const blob = new Blob([vcfContent], { type: "text/vcard;charset=utf-8;" })
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  const cleanName = (record.name || "contact").toLowerCase().replace(/[^a-z0-9]/g, "_")
  link.href = url
  link.setAttribute("download", `${cleanName}.vcf`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// Export records array to clean CSV with proper quotes and UTF-8 BOM
export function exportToCSV(records, filename = "directory_export.csv") {
  if (!records || records.length === 0) return

  const headers = ["ID", "Name", "Category", "Contact", "Email", "Address", "Notes", "Created At"]
  const rows = records.map(r => [
    r.id || "",
    `"${(r.name || "").replace(/"/g, '""')}"`,
    `"${(r.category || "General").replace(/"/g, '""')}"`,
    `"${r.contact || ""}"`,
    `"${(r.email || "").replace(/"/g, '""')}"`,
    `"${(r.address || "").replace(/"/g, '""')}"`,
    `"${(r.notes || "").replace(/"/g, '""')}"`,
    r.created_at || ""
  ])

  const csvContent = "\uFEFF" + [headers.join(","), ...rows.map(e => e.join(","))].join("\r\n")
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.setAttribute("download", filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// LocalStorage helpers for preview/dummy records on localhost
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
  // Return clean empty array - no dummy seed records
  return []
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
