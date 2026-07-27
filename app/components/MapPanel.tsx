"use client"

import { useEffect, useRef } from "react"
import { Map as MapLibreMap } from "maplibre-gl"

type MapPanelProps = {
  coordinate: [number, number]
  uncertaintyMeters: number
  selectedProvider: string
}

export function MapPanel({
  coordinate,
  uncertaintyMeters,
  selectedProvider,
}: MapPanelProps) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const mapRef = useRef<MapLibreMap | null>(null)

  useEffect(() => {
    if (!containerRef.current) return

    const map = new MapLibreMap({
      container: containerRef.current,
      center: coordinate,
      zoom: 14.6,
      attributionControl: false,
      style: {
        version: 8,
        sources: {
          context: {
            type: "geojson",
            data: {
              type: "FeatureCollection",
              features: [
                {
                  type: "Feature",
                  properties: { kind: "water" },
                  geometry: {
                    type: "Polygon",
                    coordinates: [[
                      [13.393, 52.515],
                      [13.417, 52.515],
                      [13.417, 52.518],
                      [13.393, 52.521],
                      [13.393, 52.515],
                    ]],
                  },
                },
                {
                  type: "Feature",
                  properties: { kind: "road" },
                  geometry: {
                    type: "LineString",
                    coordinates: [
                      [13.392, 52.523],
                      [13.4, 52.521],
                      [13.408, 52.5205],
                      [13.418, 52.518],
                    ],
                  },
                },
                {
                  type: "Feature",
                  properties: { kind: "boundary" },
                  geometry: {
                    type: "LineString",
                    coordinates: [
                      [13.405, 52.514],
                      [13.404, 52.526],
                    ],
                  },
                },
              ],
            },
          },
          observation: {
            type: "geojson",
            data: {
              type: "Feature",
              properties: {},
              geometry: { type: "Point", coordinates: coordinate },
            },
          },
        },
        layers: [
          {
            id: "background",
            type: "background",
            paint: { "background-color": "#e9ece6" },
          },
          {
            id: "water",
            type: "fill",
            source: "context",
            filter: ["==", ["get", "kind"], "water"],
            paint: { "fill-color": "#cadde1", "fill-opacity": 0.8 },
          },
          {
            id: "road-case",
            type: "line",
            source: "context",
            filter: ["==", ["get", "kind"], "road"],
            paint: { "line-color": "#ffffff", "line-width": 12 },
          },
          {
            id: "road-center",
            type: "line",
            source: "context",
            filter: ["==", ["get", "kind"], "road"],
            paint: {
              "line-color": "#aab3ab",
              "line-width": 2,
              "line-dasharray": [2, 3],
            },
          },
          {
            id: "boundary",
            type: "line",
            source: "context",
            filter: ["==", ["get", "kind"], "boundary"],
            paint: {
              "line-color": "#a85d11",
              "line-width": 2,
              "line-dasharray": [3, 3],
            },
          },
          {
            id: "uncertainty",
            type: "circle",
            source: "observation",
            paint: {
              "circle-radius": Math.min(46, 14 + uncertaintyMeters * 0.45),
              "circle-color": "#145a43",
              "circle-opacity": 0.12,
              "circle-stroke-color": "#145a43",
              "circle-stroke-width": 1,
              "circle-stroke-opacity": 0.45,
            },
          },
          {
            id: "pin",
            type: "circle",
            source: "observation",
            paint: {
              "circle-radius": 7,
              "circle-color": "#145a43",
              "circle-stroke-color": "#fffefa",
              "circle-stroke-width": 3,
            },
          },
        ],
      },
    })

    mapRef.current = map
    return () => {
      map.remove()
      mapRef.current = null
    }
  }, [coordinate, uncertaintyMeters])

  return (
    <div className="map-wrap">
      <div
        ref={containerRef}
        className="map-canvas"
        aria-label="Offline map of the issue location and jurisdiction boundary"
      />
      <div className="map-overlay">
        <span className="map-label">
          {coordinate[1].toFixed(4)}, {coordinate[0].toFixed(4)}
        </span>
        <span className="map-legend">
          <span><i className="legend-dot" />Observation</span>
          <span><i className="legend-dot secondary" />Boundary</span>
        </span>
      </div>
      {selectedProvider && (
        <span className="sr-only">Selected provider is {selectedProvider}</span>
      )}
    </div>
  )
}
