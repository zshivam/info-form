// Unified API configuration
// Points to your live Vercel backend deployment: https://api-zghu.vercel.app
export const API_BASE_URL = (
  import.meta.env.VITE_API_URL || 'https://api-zghu.vercel.app'
).replace(/\/+$/, '');

/**
 * Returns full URL for an image (handles Base64 data URIs, absolute URLs, or static uploads)
 * @param {string} filename 
 * @returns {string}
 */
export function getImageUrl(filename) {
  if (!filename) return '';
  if (
    filename.startsWith('http://') ||
    filename.startsWith('https://') ||
    filename.startsWith('blob:') ||
    filename.startsWith('data:')
  ) {
    return filename;
  }
  return `${API_BASE_URL}/uploads/${filename}`;
}
