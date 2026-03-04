export default function SecHead({ icon: Icon, label, c = "#6366F1", bg = "#EEF2FF" }) {
    return (
        <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 8, flexShrink: 0 }}>
            <div style={{ width: 24, height: 24, borderRadius: 7, background: bg, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Icon size={13} color={c} />
            </div>
            <span style={{ fontSize: 12, fontWeight: 700, color: "#1E293B" }}>{label}</span>
        </div>
    );
}
