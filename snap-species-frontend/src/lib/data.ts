import type { Sighting } from './types'; // assuming your Sighting interface

const now = Date.now();

export const SAMPLE_SIGHTINGS: Sighting[] = [
  {
    id: 1,
    name: 'Amur Leopard',
    sci: 'Panthera pardus orientalis',
    status: 'CR',
    lat: 43.2,
    lng: 131.8,
    timestamp: now - 2 * 60 * 1000, // 2 minutes ago
    threat_score: 97.3,
    reporter: 'field_user_42'
  },
  {
    id: 2,
    name: 'Sumatran Tiger',
    sci: 'Panthera tigris sumatrae',
    status: 'CR',
    lat: -3.5,
    lng: 102.3,
    timestamp: now - 18 * 60 * 1000, // 18 minutes ago
    threat_score: 94.1,
    reporter: 'eco_watch'
  },
  {
    id: 3,
    name: 'Black Rhinoceros',
    sci: 'Diceros bicornis',
    status: 'CR',
    lat: -3.0,
    lng: 37.3,
    timestamp: now - 1 * 60 * 60 * 1000, // 1 hour ago
    threat_score: 91.8,
    reporter: 'safari_data'
  },
  {
    id: 4,
    name: 'African Wild Dog',
    sci: 'Lycaon pictus',
    status: 'EN',
    lat: -19.5,
    lng: 34.2,
    timestamp: now - 3 * 60 * 60 * 1000, // 3 hours ago
    threat_score: 88.2,
    reporter: 'wild_tracker'
  },
  {
    id: 5,
    name: 'Snow Leopard',
    sci: 'Panthera uncia',
    status: 'VU',
    lat: 27.9,
    lng: 86.9,
    timestamp: now - 5 * 60 * 60 * 1000, // 5 hours ago
    threat_score: 95.6,
    reporter: 'himalaya_obs'
  },
  {
    id: 6,
    name: 'Giant Panda',
    sci: 'Ailuropoda melanoleuca',
    status: 'VU',
    lat: 31.2,
    lng: 103.9,
    timestamp: now - 7 * 60 * 60 * 1000, // 7 hours ago
    threat_score: 99.1,
    reporter: 'panda_watch'
  },
  {
    id: 7,
    name: 'Mountain Gorilla',
    sci: 'Gorilla beringei beringei',
    status: 'EN',
    lat: -1.4,
    lng: 29.5,
    timestamp: now - 9 * 60 * 60 * 1000, // 9 hours ago
    threat_score: 92.7,
    reporter: 'virunga_obs'
  },
  {
    id: 8,
    name: 'Vaquita',
    sci: 'Phocoena sinus',
    status: 'CR',
    lat: 31.0,
    lng: -114.7,
    timestamp: now - 12 * 60 * 60 * 1000, // 12 hours ago
    threat_score: 78.4,
    reporter: 'ocean_scout'
  },
  {
    id: 9,
    name: 'Javan Rhino',
    sci: 'Rhinoceros sondaicus',
    status: 'CR',
    lat: -6.7,
    lng: 105.3,
    timestamp: now - 1 * 24 * 60 * 60 * 1000, // 1 day ago
    threat_score: 83.9,
    reporter: 'ujung_field'
  },
  {
    id: 10,
    name: 'Siberian Crane',
    sci: 'Leucogeranus leucogeranus',
    status: 'LC',
    lat: 55.0,
    lng: 68.0,
    timestamp: now - 2 * 24 * 60 * 60 * 1000, // 2 days ago
    threat_score: 96.2,
    reporter: 'bird_net'
  }
] as Sighting[];