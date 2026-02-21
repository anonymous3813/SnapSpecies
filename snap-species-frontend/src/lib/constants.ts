export const STATUS = {
	CR: 'CR',
	EN: 'EN',
	VU: 'VU',
	NT: 'NT',
	LC: 'LC'
} as const;

export const STATUS_CONFIG = {
	[STATUS.CR]: {
		label: 'Critically Endangered',
		color: '#dc2626',
		bg: '#fef2f2',
		border: '#fca5a5'
	},
	[STATUS.EN]: { label: 'Endangered', color: '#d97706', bg: '#fffbeb', border: '#fcd34d' },
	[STATUS.VU]: { label: 'Vulnerable', color: '#ca8a04', bg: '#fefce8', border: '#fde047' },
	[STATUS.NT]: { label: 'Near Threatened', color: '#0284c7', bg: '#f0f9ff', border: '#7dd3fc' },
	[STATUS.LC]: { label: 'Least Concern', color: '#16a34a', bg: '#f0fdf4', border: '#86efac' }
} as const;
