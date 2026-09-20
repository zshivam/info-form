// Unified API configuration for Info Form
export const API_BASE_URL = (
  import.meta.env.VITE_API_URL || 'https://info-form-production.up.railway.app'
).replace(/\/+$/, '');

/**
 * Returns full URL for an uploaded file
 * @param {string} filename 
 * @returns {string}
 */
export function getImageUrl(filename) {
  if (!filename) return '';
  if (filename.startsWith('http://') || filename.startsWith('https://') || filename.startsWith('blob:')) {
    return filename;
  }
  return `${API_BASE_URL}/uploads/${filename}`;
}
