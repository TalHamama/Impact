import { ST } from "../data/mockData";
import { useState } from "react";
import { Plus, Minus, RotateCcw } from "lucide-react";

export default function RelMap({ sel, nodes, edges }) {
    const [zoom, setZoom] = useState(1);

    if (!sel) return (
        <div style={{
            width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center",
            color: "#9CA3AF", fontSize: 12, background: "#F9FAFB", borderRadius: 10
        }}>
            בחר NODE לצפייה בקישורים
        </div>
    );

    // Dynamic scaling based on zoom
    const CR = 20 * zoom;  // center radius
    const NR = 14 * zoom;  // normal radius
    const PAD = 36 * zoom; // label padding below node
    const HGAP = 62 * zoom; // horizontal gap between nodes in a row
    const VGAP = 80 * zoom; // vertical gap between rows
    const SIDE_PAD = 40 * zoom; // left/right padding

    const deps = edges.filter(e => e.t === sel.id && e.kind === "DEPENDENCY").map(e => nodes.find(n => n.id === e.s)).filter(Boolean);
    const alts = edges.filter(e => (e.s === sel.id || e.t === sel.id) && e.kind === "ALTERNATIVE").map(e => nodes.find(n => n.id === (e.s === sel.id ? e.t : e.s))).filter(Boolean);
    const imps = edges.filter(e => e.s === sel.id && e.kind === "IMPACTS").map(e => nodes.find(n => n.id === e.t)).filter(Boolean);
    const depth2 = imps.flatMap(d =>
        edges.filter(e => e.s === d.id && e.kind === "IMPACTS").map(e => ({ from: d, node: nodes.find(n => n.id === e.t) })).filter(x => x.node)
    );

    // Vertical Row Calculation (excluding alternatives)
    let rows = [];
    let y = PAD;
    if (deps.length) { rows.push({ type: "dep", y }); y += VGAP; }
    rows.push({ type: "center", y }); y += VGAP;
    if (imps.length) { rows.push({ type: "imp", y }); y += VGAP; }
    if (depth2.length) { rows.push({ type: "d2", y }); y += VGAP; }
    const H = Math.max(y + PAD, 400);

    // Width Calculation: Account for center + side alternatives
    const rowMax = Math.max(deps.length, imps.length, depth2.length, 1);
    const W = Math.max((rowMax + alts.length * 2) * HGAP, 400) + SIDE_PAD * 2;

    const rowY = (type) => rows.find(r => r.type === type)?.y ?? 0;

    const rowXs = (count) => {
        if (count === 0) return [];
        const total = (count - 1) * HGAP;
        const startX = W / 2 - total / 2;
        return Array.from({ length: count }, (_, i) => startX + i * HGAP);
    };

    const cx = W / 2;
    const cy = rowY("center");
    const depXs = rowXs(deps.length);
    const impXs = rowXs(imps.length);

    // Position alternatives horizontally to the left or right of center
    const altXs = alts.map((_, i) => {
        const side = i % 2 === 0 ? 1 : -1;
        const mult = Math.floor(i / 2) + 1;
        return cx + (side * mult * HGAP * 1.5);
    });

    const d2Positions = depth2.map(({ from, node }, i) => {
        const fi = imps.findIndex(d => d.id === from.id);
        const fpx = impXs[fi] ?? cx;
        const sf = depth2.filter(x => x.from.id === from.id);
        const idx = sf.findIndex(x => x.node.id === node.id);
        const x = fpx + (idx - (sf.length - 1) / 2) * HGAP;
        return { x, y: rowY("d2"), from, node };
    });

    function line(x1, y1, x2, y2, r1, r2, color, dash, mend) {
        const dx = x2 - x1, dy = y2 - y1, len = Math.sqrt(dx * dx + dy * dy);
        if (len < 1) return null;
        const nx = dx / len, ny = dy / len;
        return <line x1={x1 + nx * r1} y1={y1 + ny * r1} x2={x2 - nx * (r2 + 6 * zoom)} y2={y2 - ny * (r2 + 6 * zoom)}
            stroke={color} strokeWidth={1.8 * zoom} strokeDasharray={dash || "none"} markerEnd={mend} />;
    }

    function NodeCircle({ nd, x, y, r }) {
        const s = ST[nd.status];
        const dot = nd.effortColor || s.dot;
        const str = nd.effortColor || s.c;
        const isC = r === CR;
        return (
            <g>
                <circle cx={x} cy={y} r={r + 6 * zoom} fill={nd.effortColor ? `${nd.effortColor}0D` : s.bg} opacity=".7" />
                <circle cx={x} cy={y} r={r} fill="white" stroke={str} strokeWidth={isC ? 2.5 * zoom : 1.8 * zoom}
                    style={{ filter: `drop-shadow(0 ${isC ? 3 : 1}px ${isC ? 10 : 4}px rgba(0,0,0,${isC ? .15 : .1}))` }} />
                <circle cx={x} cy={y} r={isC ? 7 * zoom : 4.5 * zoom} fill={dot} />
                <text x={x} y={y + r + 13 * zoom} textAnchor="middle" fontSize={isC ? 10 * zoom : 9 * zoom}
                    fill={isC ? "#1E293B" : "#374151"} fontFamily="'Heebo',sans-serif" fontWeight={isC ? "700" : "500"}>
                    {nd.short}
                </text>
            </g>
        );
    }

    return (
        <div style={{ width: "100%", height: "100%", background: "#F9FAFB", overflow: "hidden", position: "relative" }}>
            {/* Zoom Controls Overlay */}
            <div style={{
                position: "absolute", top: 12, left: 12, display: "flex", flexDirection: "column", gap: 6, zIndex: 10,
                background: "white", padding: 5, borderRadius: 10, border: "1px solid #E2E8F0", boxShadow: "0 4px 12px rgba(0,0,0,0.06)"
            }}>
                <button onClick={() => setZoom(z => Math.min(z + 0.2, 2.5))} className="hvr" style={{ width: 30, height: 30, display: "flex", alignItems: "center", justifyContent: "center", border: "none", background: "#F8FAFC", borderRadius: 6, color: "#64748B" }}>
                    <Plus size={16} />
                </button>
                <button onClick={() => setZoom(z => Math.max(z - 0.2, 0.4))} className="hvr" style={{ width: 30, height: 30, display: "flex", alignItems: "center", justifyContent: "center", border: "none", background: "#F8FAFC", borderRadius: 6, color: "#64748B" }}>
                    <Minus size={16} />
                </button>
                <div style={{ height: 1, background: "#F1F5F9", margin: "2px 4px" }} />
                <button onClick={() => setZoom(1)} className="hvr" style={{ width: 30, height: 30, display: "flex", alignItems: "center", justifyContent: "center", border: "none", background: "#F8FAFC", borderRadius: 6, color: "#64748B" }}>
                    <RotateCcw size={14} />
                </button>
            </div>

            <div style={{ width: "100%", height: "100%", overflow: "auto", cursor: "grab" }}>
                <svg width={Math.max(W, 300)} height={Math.max(H, 400)} viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet" style={{ display: "block" }}>
                    <defs>
                        {[["ri", "#EF4444"], ["rd", "#6366F1"], ["ra", "#F59E0B"]].map(([id, c]) => (
                            <marker key={id} id={`rr-${id}`} markerWidth={6 * zoom} markerHeight={6 * zoom} refX={5 * zoom} refY={3 * zoom} orient="auto">
                                <path d="M0,0 L0,6 L6,3z" fill={c} transform={`scale(${zoom})`} />
                            </marker>
                        ))}
                    </defs>
                    <rect width={W} height={H} fill="#F9FAFB" />

                    {/* Lines */}
                    {deps.map((nd, i) => line(depXs[i], rowY("dep"), cx, cy, NR, CR, "#6366F1", "none", "url(#rr-rd)"))}
                    {alts.map((nd, i) => line(altXs[i], cy, cx, cy, NR, CR, "#F59E0B", "5,3", "url(#rr-ra)"))}
                    {imps.map((nd, i) => line(cx, cy, impXs[i], rowY("imp"), CR, NR, "#EF4444", "none", "url(#rr-ri)"))}
                    {d2Positions.map(({ from, node, x, y }, i) => {
                        const fi = imps.findIndex(d => d.id === from.id);
                        const fpx = impXs[fi] ?? cx;
                        return line(fpx, rowY("imp"), x, y, NR, NR, "#EF4444", "4,3", "url(#rr-ri)");
                    })}

                    {/* Nodes */}
                    {deps.map((nd, i) => <NodeCircle key={`dep${i}`} nd={nd} x={depXs[i]} y={rowY("dep")} r={NR} />)}
                    {alts.map((nd, i) => <NodeCircle key={`alt${i}`} nd={nd} x={altXs[i]} y={cy} r={NR} />)}
                    <NodeCircle nd={sel} x={cx} y={cy} r={CR} />
                    {imps.map((nd, i) => <NodeCircle key={`imp${i}`} nd={nd} x={impXs[i]} y={rowY("imp")} r={NR} />)}
                    {d2Positions.map(({ node, x, y }, i) => <NodeCircle key={`d2-${i}`} nd={node} x={x} y={y} r={NR} />)}

                    {/* Labels */}
                    {deps.length > 0 && <text x={W - 10} y={rowY("dep") + 4 * zoom} textAnchor="end" fontSize={8 * zoom} fill="#6366F1" opacity=".55" fontFamily="'Heebo',sans-serif">תלות</text>}
                    {alts.length > 0 && <text x={W - 10} y={cy + 4 * zoom} textAnchor="end" fontSize={8 * zoom} fill="#F59E0B" opacity=".55" fontFamily="'Heebo',sans-serif">חלופות</text>}
                    {imps.length > 0 && <text x={W - 10} y={rowY("imp") + 4 * zoom} textAnchor="end" fontSize={8 * zoom} fill="#EF4444" opacity=".55" fontFamily="'Heebo',sans-serif">השפעה</text>}
                    {depth2.length > 0 && <text x={W - 10} y={rowY("d2") + 4 * zoom} textAnchor="end" fontSize={8 * zoom} fill="#EF4444" opacity=".4" fontFamily="'Heebo',sans-serif">השפעה עקיפה</text>}
                </svg>
            </div>
        </div>
    );
}
