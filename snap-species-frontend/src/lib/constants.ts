export const ANIMAL_STATUS = {
	CR: 'CR',
	EN: 'EN',
	VU: 'VU',
	NT: 'NT',
	LC: 'LC'
} as const;

export const STATUS_CONFIG = {
  CR: { label: 'Critically Endangered', color: '#dc2626', bg: '#fef2f2', border: '#fca5a5', ring: '#fee2e2' },
  EN: { label: 'Endangered',            color: '#d97706', bg: '#fffbeb', border: '#fcd34d', ring: '#fef3c7' },
  VU: { label: 'Vulnerable',            color: '#ca8a04', bg: '#fefce8', border: '#fde047', ring: '#fef9c3' },
  NT: { label: 'Near Threatened',       color: '#0284c7', bg: '#f0f9ff', border: '#7dd3fc', ring: '#e0f2fe' },
  LC: { label: 'Least Concern',         color: '#16a34a', bg: '#f0fdf4', border: '#86efac', ring: '#dcfce7' },
} as const;

export type StatusKey = keyof typeof STATUS_CONFIG;