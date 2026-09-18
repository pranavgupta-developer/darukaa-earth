/**
 * Interactive Mapbox GL JS map component.
 *
 * Renders site polygons from GeoJSON FeatureCollection,
 * supports polygon drawing mode via @mapbox/mapbox-gl-draw,
 * and handles site click selection with popups.
 */

import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import MapboxDraw from '@mapbox/mapbox-gl-draw';
import 'mapbox-gl/dist/mapbox-gl.css';
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';
import type { GeoJSONFeatureCollection, GeoJSONPolygon } from '../../types';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || '';

interface MapViewProps {
  geojson: GeoJSONFeatureCollection | null;
  isDrawing: boolean;
  onPolygonDrawn: (polygon: GeoJSONPolygon) => void;
  onSiteClick: (siteId: string) => void;
  selectedSiteId: string | null;
}

const MapView: React.FC<MapViewProps> = ({
  geojson,
  isDrawing,
  onPolygonDrawn,
  onSiteClick,
  selectedSiteId,
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const draw = useRef<MapboxDraw | null>(null);
  const popup = useRef<mapboxgl.Popup | null>(null);
  const [mapReady, setMapReady] = useState(false);

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    const newMap = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/satellite-streets-v12',
      center: [78.9629, 20.5937], // India center
      zoom: 4,
    });

    newMap.addControl(new mapboxgl.NavigationControl(), 'top-right');
    newMap.addControl(new mapboxgl.FullscreenControl(), 'top-right');

    // Initialize draw control
    const drawControl = new MapboxDraw({
      displayControlsDefault: false,
      controls: {},
      defaultMode: 'simple_select',
    });
    newMap.addControl(drawControl as unknown as mapboxgl.IControl);
    draw.current = drawControl;

    newMap.on('load', () => {
      setMapReady(true);

      // Add site polygons source and layers
      newMap.addSource('sites', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
      });

      newMap.addLayer({
        id: 'sites-fill',
        type: 'fill',
        source: 'sites',
        paint: {
          'fill-color': [
            'case',
            ['boolean', ['feature-state', 'selected'], false],
            '#00d4aa',
            '#0ea5e9',
          ],
          'fill-opacity': 0.3,
        },
      });

      newMap.addLayer({
        id: 'sites-border',
        type: 'line',
        source: 'sites',
        paint: {
          'line-color': [
            'case',
            ['boolean', ['feature-state', 'selected'], false],
            '#00d4aa',
            '#0ea5e9',
          ],
          'line-width': 2,
        },
      });

      // Click handler for site polygons
      newMap.on('click', 'sites-fill', (e) => {
        if (e.features && e.features.length > 0) {
          const feature = e.features[0];
          const siteId = feature.properties?.id;
          if (siteId) {
            onSiteClick(siteId);

            // Show popup
            const name = feature.properties?.name || 'Site';
            const area = feature.properties?.area_hectares;

            if (popup.current) popup.current.remove();
            popup.current = new mapboxgl.Popup({ closeOnClick: true, offset: 15 })
              .setLngLat(e.lngLat)
              .setHTML(
                `<div class="map-popup">
                  <strong>${name}</strong>
                  ${area ? `<br/><span>${Number(area).toFixed(1)} hectares</span>` : ''}
                  <br/><em class="popup-hint">Click to view analytics</em>
                </div>`,
              )
              .addTo(newMap);
          }
        }
      });

      // Cursor change on hover
      newMap.on('mouseenter', 'sites-fill', () => {
        newMap.getCanvas().style.cursor = 'pointer';
      });
      newMap.on('mouseleave', 'sites-fill', () => {
        newMap.getCanvas().style.cursor = '';
      });
    });

    // Handle draw create event
    newMap.on('draw.create', (e: { features: GeoJSON.Feature[] }) => {
      if (e.features.length > 0) {
        const feature = e.features[0];
        if (feature.geometry.type === 'Polygon') {
          onPolygonDrawn(feature.geometry as GeoJSONPolygon);
          // Remove drawn feature from draw control
          drawControl.deleteAll();
        }
      }
    });

    map.current = newMap;

    return () => {
      newMap.remove();
      map.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Update GeoJSON data
  useEffect(() => {
    if (!map.current || !mapReady || !geojson) return;

    const source = map.current.getSource('sites') as mapboxgl.GeoJSONSource | undefined;
    if (source) {
      source.setData(geojson as unknown as GeoJSON.FeatureCollection);

      // Fit bounds to features if any
      if (geojson.features.length > 0) {
        const bounds = new mapboxgl.LngLatBounds();
        geojson.features.forEach((feature) => {
          feature.geometry.coordinates[0].forEach((coord) => {
            bounds.extend(coord as [number, number]);
          });
        });
        map.current?.fitBounds(bounds, { padding: 60, maxZoom: 14 });
      }
    }
  }, [geojson, mapReady]);

  // Toggle draw mode
  useEffect(() => {
    if (!draw.current) return;
    if (isDrawing) {
      draw.current.changeMode('draw_polygon');
    } else {
      draw.current.changeMode('simple_select');
      draw.current.deleteAll();
    }
  }, [isDrawing]);

  // Highlight selected site
  useEffect(() => {
    if (!map.current || !mapReady || !geojson) return;

    // Remove previous selection state
    geojson.features.forEach((feature) => {
      map.current?.setFeatureState(
        { source: 'sites', id: feature.id },
        { selected: false },
      );
    });

    // Set new selection
    if (selectedSiteId) {
      map.current.setFeatureState(
        { source: 'sites', id: selectedSiteId },
        { selected: true },
      );
    }
  }, [selectedSiteId, geojson, mapReady]);

  return (
    <div className="map-view">
      {!MAPBOX_TOKEN && (
        <div className="map-error">
          <p>⚠️ Mapbox token not configured. Set VITE_MAPBOX_TOKEN in your .env file.</p>
        </div>
      )}
      <div ref={mapContainer} className="map-canvas" />
    </div>
  );
};

export default MapView;
