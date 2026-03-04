import { Filter, X, MapPin } from "lucide-react";

export default function FilterBar({ filters, toggleF, typeF, setTypeF, sel, setSel }) {
    const filterOptions = [
        { k: "dependency", l: "תלות", c: "#6366F1", dash: "none" },
        { k: "alternative", l: "חלופה", c: "#F59E0B", dash: "7,3" },
        { k: "impacts", l: "השפעה", c: "#EF4444", dash: "4,2" }
    ];

    const typeOptions = [
        { id: "all", l: "הכל" },
        { id: "A", l: "A" },
        { id: "B", l: "תחנות" },
        { id: "C", l: "מאמצים" }
    ];

    return (
        <div style={{
            background: "white", borderBottom: "1px solid #E2E8F0", padding: "8px 16px",
            display: "flex", gap: 7, alignItems: "center", flexShrink: 0, flexWrap: "wrap"
        }}>
            <Filter size={12} color="#6366F1" />
            <span style={{ fontSize: 11, color: "#6B7280", fontWeight: 700 }}>קשרים:</span>
            {filterOptions.map(({ k, l, c, dash }) => (
                <button key={k} onClick={() => toggleF(k)} style={{
                    padding: "4px 12px", borderRadius: 16, fontSize: 11, fontWeight: 600, cursor: "pointer",
                    background: filters[k] ? `${c}14` : "#F8FAFC", color: filters[k] ? c : "#94A3B8",
                    border: `1.5px solid ${filters[k] ? c : "#E2E8F0"}`,
                    display: "flex", alignItems: "center", gap: 6, transition: "all .14s"
                }}>
                    <svg width="16" height="4"><line x1="0" y1="2" x2="16" y2="2"
                        stroke={filters[k] ? c : "#CBD5E1"} strokeWidth="2" strokeDasharray={dash} /></svg>{l}
                </button>
            ))}
            <div style={{ width: 1, height: 20, background: "#E2E8F0", margin: "0 2px" }} />
            <span style={{ fontSize: 11, color: "#6B7280", fontWeight: 700 }}>סוג:</span>
            {typeOptions.map(t => (
                <button key={t.id} onClick={() => setTypeF(t.id)} style={{
                    padding: "4px 11px", borderRadius: 16, fontSize: 11, fontWeight: 600, cursor: "pointer",
                    background: typeF === t.id ? "#6366F1" : "#F8FAFC",
                    color: typeF === t.id ? "white" : "#6B7280",
                    border: `1.5px solid ${typeF === t.id ? "#6366F1" : "#E2E8F0"}`, transition: "all .14s"
                }}>{t.l}</button>
            ))}
            {sel && <button onClick={() => setSel(null)} style={{
                marginRight: "auto", background: "#F8FAFC",
                border: "1px solid #E2E8F0", borderRadius: 8, padding: "4px 10px", fontSize: 11, color: "#6B7280",
                display: "flex", alignItems: "center", gap: 5, cursor: "pointer"
            }}><X size={11} />חזור למפה מלאה</button>}
            {!sel && <div style={{ marginRight: "auto", fontSize: 11, color: "#94A3B8", display: "flex", alignItems: "center", gap: 5 }}><MapPin size={11} />לחץ על NODE לפרטים</div>}
        </div>
    );
}
