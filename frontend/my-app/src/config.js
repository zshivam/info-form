// Unified API configuration
// If VITE_API_URL is specified (e.g. for local dev http://localhost:8000), use it.
// Otherwise, on Vercel full-stack deployment, empty string '' means same-origin relative requests (/api or /submit), eliminating CORS completely!
export const API_BASE_URL = (
  import.meta.env.VITE_API_URL !== undefined
    ? import.meta.env.VITE_API_URL
    : ''
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
