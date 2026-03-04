import { MapContainer, TileLayer, Marker, Polyline, useMap } from "react-leaflet";
import L from "leaflet";
import { ST, ECFG } from "../data/mockData";
import { useEffect } from "react";

// Fix for default Leaflet icon issue in React
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

let DefaultIcon = L.icon({
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

// Custom Dot Icon creator
const createCustomIcon = (nd, isSel) => {
    const s = ST[nd.status];
    const size = isSel ? 34 : 26;
    const innerSize = isSel ? 10 : 7;

    return L.divIcon({
        className: "custom-marker",
        html: `
            <div style="
                width: ${size}px; 
                height: ${size}px; 
                background: white; 
                border: ${isSel ? 3 : 2}px solid ${s.c}; 
                border-radius: 50%; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                position: relative;
            ">
                <div style="width: ${innerSize}px; height: ${innerSize}px; background: ${s.dot}; border-radius: 50%;"></div>
                <div style="
                    position: absolute; 
                    left: ${size + 4}px; 
                    background: white; 
                    padding: 2px 8px; 
                    border-radius: 6px; 
                    border: 1px solid ${isSel ? s.c : "#E5E7EB"};
                    font-size: 11px;
                    font-weight: ${isSel ? 800 : 600};
                    color: ${isSel ? s.c : "#374151"};
                    white-space: nowrap;
                    pointer-events: none;
                ">${nd.label}</div>
            </div>
        `,
        iconSize: [size, size],
        iconAnchor: [size / 2, size / 2]
    });
};

function MapResizer({ selected }) {
    const map = useMap();
    useEffect(() => {
        map.invalidateSize();
        if (selected && selected.lat && selected.lng) {
            map.setView([selected.lat, selected.lng], 13, { animate: true });
        }
    }, [selected, map]);
    return null;
}

export default function GeoMap({ nodes, edges, selected, onSelect, filters }) {
    const mapNodes = nodes.filter(n => n.onMap);

    const visEdges = edges.filter(e => {
        if (!filters[e.kind.toLowerCase()]) return false;
        const sn = nodes.find(n => n.id === e.s), tn = nodes.find(n => n.id === e.t);
        return sn?.onMap && tn?.onMap;
    });

    const center = selected?.onMap ? [selected.lat, selected.lng] : [32.08, 34.80];

    return (
        <div style={{ width: "100%", height: "100%", position: "relative" }}>
            <MapContainer
                center={center}
                zoom={12}
                style={{ width: "100%", height: "100%", background: "#f0f0f0" }}
                zoomControl={false}
            >
                <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                />

                <MapResizer selected={selected} />

                {/* Draw Edges */}
                {visEdges.map((e) => {
                    const a = nodes.find(n => n.id === e.s);
                    const b = nodes.find(n => n.id === e.t);
                    if (!a || !b) return null;
                    const ec = ECFG[e.kind];
                    return (
                        <Polyline
                            key={e.id}
                            positions={[[a.lat, a.lng], [b.lat, b.lng]]}
                            color={ec.color}
                            weight={ec.w + 1}
                            dashArray={ec.dash !== "none" ? ec.dash : undefined}
                            opacity={0.7}
                        />
                    );
                })}

                {/* Draw Nodes */}
                {mapNodes.map((nd) => {
                    const isSel = selected?.id === nd.id;
                    return (
                        <Marker
                            key={nd.id}
                            position={[nd.lat, nd.lng]}
                            icon={createCustomIcon(nd, isSel)}
                            eventHandlers={{
                                click: () => onSelect(nd)
                            }}
                        />
                    );
                })}
            </MapContainer>

            {/* Legend Overlay */}
            <div style={{
                position: "absolute", bottom: 12, left: 12, zIndex: 1000,
                background: "white", padding: "8px 12px", borderRadius: 10,
                border: "1px solid #E2E8F0", boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
                display: "flex", gap: 15
            }}>
                {Object.entries(ECFG).map(([k, v]) => (
                    <div key={k} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                        <div style={{
                            width: 20, height: 2, background: v.color,
                            borderTop: v.dash !== "none" ? `2px dashed ${v.color}` : "none"
                        }} />
                        <span style={{ fontSize: 10, color: "#64748B", fontWeight: 600 }}>{v.label}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}
