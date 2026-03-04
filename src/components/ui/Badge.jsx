import { ST } from "../../data/mockData";

export default function Badge({ status, small }) {
    const s = ST[status];
    const Icon = s.Icon;
    return (
        <span style={{
            display: "inline-flex", alignItems: "center", gap: 4, background: s.bg, color: s.c,
            border: `1px solid ${s.bd}`, borderRadius: 20, padding: small ? "2px 8px" : "3px 10px",
            fontSize: small ? 10 : 11, fontWeight: 700, whiteSpace: "nowrap", flexShrink: 0
        }}>
            <Icon size={small ? 10 : 12} />{s.label}
        </span>
    );
}
