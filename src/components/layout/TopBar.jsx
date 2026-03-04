import { Shield, Clock } from "lucide-react";

export default function TopBar({ nodes }) {
    const stats = [
        { l: "תקינים", v: nodes.filter(n => n.status === "active").length, c: "#15803D", bg: "#F0FDF4", bd: "#BBF7D0" },
        { l: "תקלה", v: nodes.filter(n => n.status === "warning").length, c: "#B45309", bg: "#FFFBEB", bd: "#FDE68A" },
        { l: "כשל", v: nodes.filter(n => n.status === "failed").length, c: "#DC2626", bg: "#FEF2F2", bd: "#FECACA" }
    ];

    return (
        <div style={{
            background: "white", borderBottom: "1px solid #E2E8F0", padding: "0 18px", height: 50,
            display: "flex", alignItems: "center", justifyContent: "space-between", flexShrink: 0
        }}>
            <div style={{ display: "flex", alignItems: "center", gap: 11 }}>
                <div style={{ width: 32, height: 32, borderRadius: 9, background: "#EEF2FF", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <Shield size={16} color="#6366F1" />
                </div>
                <div>
                    <div style={{ fontSize: 14, fontWeight: 800, color: "#1E293B" }}>מערכת ניהול תלויות</div>
                    <div style={{ fontSize: 9, color: "#94A3B8" }}>Dependency Management System</div>
                </div>
            </div>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                {stats.map(({ l, v, c, bg, bd }) => (
                    <div key={l} style={{ background: bg, border: `1px solid ${bd}`, borderRadius: 18, padding: "2px 11px", display: "flex", gap: 5, alignItems: "center" }}>
                        <span style={{ fontSize: 15, fontWeight: 800, color: c, lineHeight: 1 }}>{v}</span>
                        <span style={{ fontSize: 10, fontWeight: 600, color: c }}>{l}</span>
                    </div>
                ))}
                <div style={{ fontSize: 10, color: "#94A3B8", display: "flex", alignItems: "center", gap: 3 }}>
                    <Clock size={11} />{new Date().toLocaleTimeString("he-IL")}
                </div>
            </div>
        </div>
    );
}
