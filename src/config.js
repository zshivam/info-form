// Unified API configuration for PulseDesk Directory Hub

export const isLocalPreview = typeof window !== 'undefined' && (
  window.location.hostname === 'localhost' || 
  window.location.hostname === '127.0.0.1' ||
  window.location.hostname.includes('192.168.')
);

// On production Vercel deployment, same-origin relative URLs (/api, /submit, /records) avoid all CORS issues
export const API_BASE_URL = (
  import.meta.env.VITE_API_URL || (typeof window !== 'undefined' && !isLocalPreview ? '' : '')
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
