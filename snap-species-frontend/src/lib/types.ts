export interface Sighting {
    id: number;
    name: string;
    sci: string;
    status: 'CR' | 'EN' | 'VU' | 'NT' | 'LC';
    lat: number;
    lng: number;
    time: string;
    conf: number;
    reporter: string;
}