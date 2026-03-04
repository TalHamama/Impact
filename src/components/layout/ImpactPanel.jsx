import { Zap, Package, Activity } from "lucide-react";
import Panel from "../ui/Panel";
import SecHead from "../ui/SecHead";
import RelMap from "../RelMap";

export default function ImpactPanel({ sel, nodes, edges, impactChips }) {
    if (!sel) return null;

    return (
        <div style={{ borderLeft: "1px solid #E2E8F0", overflow: "hidden", display: "flex", flexDirection: "column", padding: "10px", gap: 9 }}>
            {/* השפעות */}
            <Panel style={{ flexShrink: 0 }}>
                <SecHead icon={Zap} label="השפעות" c="#D97706" bg="#FEF9C3" />
                {sel.impacts.length === 0 && sel.alternatives.length === 0
                    ? <div style={{ fontSize: 11, color: "#9CA3AF", textAlign: "center", padding: "4px 0" }}>אין השפעות מוגדרות</div>
                    : <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
                        {sel.impacts.length > 0 && <>
                            <div style={{ fontSize: 10, color: "#6B7280", fontWeight: 600 }}>השפעה ישירה:</div>
                            {sel.impacts.map((im, i) => (
                                <div key={i} style={{
                                    background: "#FFFBEB", border: "1px solid #FDE68A", borderRadius: 8,
                                    padding: "5px 10px", fontSize: 11, color: "#92400E", fontWeight: 600,
                                    display: "flex", alignItems: "center", gap: 6, lineHeight: 1
                                }}>
                                    <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#F59E0B", flexShrink: 0 }} />
                                    <span style={{ display: "inline-block", paddingBottom: "1px" }}>{im}</span>
                                </div>
                            ))}
                        </>}
                        {sel.alternatives.length > 0 && (
                            <div style={{ padding: "5px 10px", background: "#F0FDF4", border: "1px solid #BBF7D0", borderRadius: 8 }}>
                                <div style={{ fontSize: 9, color: "#15803D", fontWeight: 700, marginBottom: 2 }}>✓ חלופות זמינות</div>
                                <div style={{ fontSize: 11, color: "#166534" }}>{sel.alternatives.join(" | ")}</div>
                            </div>
                        )}
                        {impactChips.filter(n => n.type === "C").length > 0 && (
                            <div>
                                <div style={{ fontSize: 10, color: "#94A3B8", fontWeight: 600, marginBottom: 4 }}>מאמצים מושפעים:</div>
                                <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                                    {impactChips.filter(n => n.type === "C").map(nd => (
                                        <span key={nd.id} style={{
                                            display: "inline-flex", alignItems: "center", gap: 5,
                                            background: `${nd.effortColor}14`, color: nd.effortColor,
                                            border: `1px solid ${nd.effortColor}44`,
                                            borderRadius: 20, padding: "3px 10px", fontSize: 10, fontWeight: 700,
                                            lineHeight: 1
                                        }}>
                                            <Package size={9} style={{ flexShrink: 0 }} />
                                            <span style={{ display: "inline-block", paddingBottom: "1px" }}>{nd.label}</span>
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                }
            </Panel>

            {/* מפת קישורים */}
            <div style={{
                flex: 1, background: "white", borderRadius: 12, border: "1px solid #E5E7EB",
                overflow: "hidden", display: "flex", flexDirection: "column", minHeight: 0,
                boxShadow: "0 1px 3px rgba(0,0,0,.05)"
            }}>
                <div style={{ padding: "9px 13px 5px", borderBottom: "1px solid #F3F4F6", flexShrink: 0 }}>
                    <SecHead icon={Activity} label="מפת קישורים" c="#15803D" bg="#F0FDF4" />
                </div>
                <div style={{ flex: 1, minHeight: 0, overflow: "hidden" }}>
                    <RelMap sel={sel} nodes={nodes} edges={edges} />
                </div>
            </div>
        </div>
    );
}
