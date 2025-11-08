<template>
    <div class="geolocation-field-wrapper">
        <div ref="mapContainer" class="map-container border rounded-md" style="min-height: 400px; z-index: 1;"></div>
        <div class="flex items-center gap-2 mt-2">
            <Button variant="outline" size="sm" @click="getCurrentLocation">
                <MapPin class="h-4 w-4 mr-2" />
                Use Current Location
            </Button>
            <Button v-if="geolocationData" variant="outline" size="sm" @click="clearLocation">
                Clear
            </Button>
        </div>
        <p v-if="geolocationData" class="text-xs text-muted-foreground mt-2">
            Location: {{ formatLocation(geolocationData) }}
        </p>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue';
import { Button } from '@/components/ui/button';
import { MapPin } from 'lucide-vue-next';
import { FormField } from '@/types/formfield';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
// @ts-ignore - leaflet-draw doesn't have types
import 'leaflet-draw';
import 'leaflet-draw/dist/leaflet.draw.css';

// Fix for default marker icons in Leaflet with Vite
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import iconRetina from 'leaflet/dist/images/marker-icon-2x.png';

const DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconRetinaUrl: iconRetina,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    tooltipAnchor: [16, -28],
    shadowSize: [41, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

const props = defineProps<{
    field: FormField;
    modelValue: string | null;
}>();

const emit = defineEmits<{
    'update:modelValue': [value: string | null];
}>();

const mapContainer = ref<HTMLDivElement | null>(null);
let map: L.Map | null = null;
let editableLayers: L.FeatureGroup | null = null;
let drawControl: L.Control.Draw | null = null;
const geolocationData = ref<string | null>(props.modelValue);

watch(() => props.modelValue, (value) => {
    geolocationData.value = value;
    if (value && map) {
        loadGeolocationData(value);
    }
}, { immediate: true });

onMounted(() => {
    nextTick(() => {
        if (mapContainer.value) {
            initializeMap();
            if (geolocationData.value) {
                loadGeolocationData(geolocationData.value);
            }
        }
    });
});

onUnmounted(() => {
    if (map) {
        map.remove();
        map = null;
    }
});

function initializeMap() {
    if (!mapContainer.value) return;
    
    // Initialize map
    map = L.map(mapContainer.value);
    map.setView([51.505, -0.09], 13); // Default to London
    
    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Initialize editable layers
    editableLayers = new L.FeatureGroup();
    editableLayers.addTo(map);
    
    // Initialize draw control
    drawControl = new L.Control.Draw({
        position: 'topleft',
        draw: {
            marker: true,
            polyline: false,
            polygon: false,
            circle: false,
            rectangle: false,
        },
        edit: {
            featureGroup: editableLayers,
            remove: true,
        },
    });
    drawControl.addTo(map);
    
    // Handle draw events
    map.on('draw:created', (e: any) => {
        const layer = e.layer;
        editableLayers?.addLayer(layer);
        updateGeolocationData();
    });
    
    map.on('draw:deleted draw:edited', () => {
        updateGeolocationData();
    });
}

function loadGeolocationData(value: string) {
    if (!map || !editableLayers) return;
    
    try {
        const geoJson = JSON.parse(value);
        editableLayers.clearLayers();
        
        L.geoJSON(geoJson, {
            onEachFeature: (feature, layer) => {
                editableLayers?.addLayer(layer);
            }
        });
        
        if (editableLayers.getLayers().length > 0) {
            map.fitBounds(editableLayers.getBounds(), { padding: [50, 50] });
        }
    } catch (error) {
        // Silently handle error - map will just be empty
    }
}

function updateGeolocationData() {
    if (!editableLayers) return;
    
    const geoJson = editableLayers.toGeoJSON();
    const geoJsonString = JSON.stringify(geoJson);
    geolocationData.value = geoJsonString;
    emit('update:modelValue', geoJsonString);
}

function getCurrentLocation() {
    if (!map) return;
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                map?.setView([latitude, longitude], 13);
                
                // Add marker at current location
                if (editableLayers) {
                    editableLayers.clearLayers();
                    const marker = L.marker([latitude, longitude]);
                    editableLayers.addLayer(marker);
                    updateGeolocationData();
                }
            },
            (error) => {
                // Silently handle error - user can manually set location
            }
        );
    }
}

function clearLocation() {
    if (editableLayers) {
        editableLayers.clearLayers();
        updateGeolocationData();
    }
}

function formatLocation(geoJsonString: string): string {
    try {
        const geoJson = JSON.parse(geoJsonString);
        if (geoJson.features && geoJson.features.length > 0) {
            const feature = geoJson.features[0];
            if (feature.geometry.type === 'Point') {
                const [lng, lat] = feature.geometry.coordinates;
                return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
            }
        }
        return 'Location set';
    } catch {
        return 'Invalid location data';
    }
}
</script>

<style scoped>
.map-container {
    position: relative;
}
</style>

