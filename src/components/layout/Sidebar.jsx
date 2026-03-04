import { Wrench, FileText, AlertCircle, AlertTriangle, CheckCircle, Zap, Package } from "lucide-react";
import { useState } from "react";
import Panel from "../ui/Panel";
import SecHead from "../ui/SecHead";
import Badge from "../ui/Badge";
import Ring from "../ui/Ring";
import { ST } from "../../data/mockData";

export default function Sidebar({ sel, onReportIncident, impactChips }) {
    const [repTxt, setRepTxt] = useState("");
    const [sent, setSent] = useState(false);

    if (!sel) return null;

    const s = ST[sel.status];

    const send = async () => {
        if (repTxt.trim()) {
            await onReportIncident(sel.id, repTxt);
            setSent(true);
            setTimeout(() => {
                setSent(false);
                setRepTxt("");
            }, 2000);
        }
    };

    return (
        <div style={{ borderLeft: "1px solid #E2E8F0", overflow: "auto", padding: "10px", display: "flex", flexDirection: "column", gap: 10, background: "#F8FAFC" }}>
            {/* תעודת זהות */}
            <Panel>
                <SecHead icon={FileText} label={`תעודת זהות — ${sel.label}`} c="#6366F1" bg="#EEF2FF" />
                <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
                    <Ring score={sel.score} c={s.c} size={52} />
                    <div style={{ flex: 1 }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 5 }}>
                            <div style={{ fontSize: 13, fontWeight: 800, color: "#1E293B" }}>{sel.label}</div>
                            <Badge status={sel.status} small />
                        </div>
                        <div style={{ fontSize: 10.5, color: "#64748B", lineHeight: 1.5, marginBottom: 7 }}>{sel.description}</div>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4px 10px" }}>
                            {[["סוג", `סוג ${sel.type}`], ["אזור", sel.zone], ["בעלים", sel.owner], ["קואורד׳", sel.coords]].map(([k, v]) => (
                                <div key={k} style={{ fontSize: 10, padding: "2px 0", borderBottom: "1px solid #F1F5F9" }}>
                                    <span style={{ color: "#94A3B8" }}>{k}: </span>
                                    <span style={{ color: "#374151", fontWeight: 700 }}>{v}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </Panel>

            {/* השפעות */}
            <Panel>
                <SecHead icon={Zap} label="השפעות וקשרים" c="#D97706" bg="#FEF9C3" />
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {sel.impacts.length > 0 && (
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                            {sel.impacts.map((im, i) => (
                                <div key={i} style={{
                                    background: "#FFFBEB", border: "1px solid #FDE68A", borderRadius: 6,
                                    padding: "4px 8px", fontSize: 10, color: "#92400E", fontWeight: 700,
                                    display: "flex", alignItems: "center", gap: 4
                                }}>
                                    <div style={{ width: 5, height: 5, borderRadius: "50%", background: "#F59E0B" }} />
                                    {im}
                                </div>
                            ))}
                        </div>
                    )}
                    {sel.alternatives.length > 0 && (
                        <div style={{ padding: "5px 10px", background: "#F0FDF4", border: "1px solid #BBF7D0", borderRadius: 7 }}>
                            <div style={{ fontSize: 9, color: "#15803D", fontWeight: 800, marginBottom: 2 }}>✓ חלופות זמינות</div>
                            <div style={{ fontSize: 10, color: "#166534", fontWeight: 600 }}>{sel.alternatives.join(" | ")}</div>
                        </div>
                    )}
                    {impactChips.filter(n => n.type === "C").length > 0 && (
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginTop: 2 }}>
                            {impactChips.filter(n => n.type === "C").map(nd => (
                                <span key={nd.id} style={{
                                    display: "inline-flex", alignItems: "center", gap: 4,
                                    background: `${nd.effortColor}0F`, color: nd.effortColor,
                                    border: `1px solid ${nd.effortColor}33`,
                                    borderRadius: 15, padding: "3px 8px", fontSize: 9, fontWeight: 700
                                }}>
                                    <Package size={8} />
                                    {nd.label}
                                </span>
                            ))}
                        </div>
                    )}
                    {sel.impacts.length === 0 && sel.alternatives.length === 0 && impactChips.length === 0 && (
                        <div style={{ fontSize: 10, color: "#9CA3AF", textAlign: "center" }}>אין השפעות ישירות</div>
                    )}
                </div>
            </Panel>

            {/* טיפול */}
            <Panel>
                <SecHead icon={Wrench} label="טיפול ותחזוקה" c="#059669" bg="#ECFDF5" />
                {sel.steps.length === 0
                    ? <div style={{ fontSize: 10, color: "#9CA3AF", textAlign: "center" }}>אין נוהל מוגדר</div>
                    : <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                        {sel.steps.map((step, i) => (
                            <div key={i} className="srow" style={{
                                display: "flex", gap: 7, alignItems: "center",
                                padding: "4px 6px", borderRadius: 6, transition: "background .1s"
                            }}>
                                <div style={{
                                    flexShrink: 0, width: 16, height: 16, borderRadius: "50%", background: "#ECFDF5",
                                    color: "#059669", fontSize: 9, fontWeight: 800, display: "flex", alignItems: "center", justifyContent: "center"
                                }}>{i + 1}</div>
                                <span style={{ fontSize: 10.5, color: "#374151", lineHeight: 1.3 }}>{step}</span>
                            </div>
                        ))}
                    </div>
                }
            </Panel>

            {/* דיווח תקלה */}
            <Panel>
                <SecHead icon={AlertCircle} label="דיווח ותחקירי אירוע" c="#DC2626" bg="#FEF2F2" />
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {sel.incidents.map((inc, i) => (
                        <div key={i} className="srow" style={{
                            display: "flex", gap: 8, padding: "6px 4px",
                            borderBottom: i < sel.incidents.length - 1 ? "1px solid #F1F5F9" : "none", borderRadius: 6
                        }}>
                            <div style={{
                                width: 24, height: 24, borderRadius: 6, flexShrink: 0,
                                background: inc.status === "בטיפול" ? "#FFFBEB" : "#F0FDF4",
                                display: "flex", alignItems: "center", justifyContent: "center"
                            }}>
                                {inc.status === "בטיפול" ? <AlertTriangle size={12} color="#D97706" /> : <CheckCircle size={12} color="#15803D" />}
                            </div>
                            <div style={{ flex: 1 }}>
                                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 1 }}>
                                    <span style={{ fontSize: 10, fontWeight: 700, color: "#1E293B" }}>{inc.reporter}</span>
                                    <span style={{ fontSize: 8.5, color: "#94A3B8" }}>{inc.date}</span>
                                </div>
                                <div style={{ fontSize: 9.5, color: "#64748B", lineHeight: 1.3 }}>{inc.desc}</div>
                            </div>
                        </div>
                    ))}
                    {sent
                        ? <div style={{ display: "flex", alignItems: "center", gap: 6, color: "#15803D", fontSize: 11, fontWeight: 700, padding: "10px 0", justifyContent: "center" }}>
                            <CheckCircle size={14} />נשלח למערכת בהצלחה
                        </div>
                        : <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 4 }}>
                            <textarea value={repTxt} onChange={e => setRepTxt(e.target.value)} rows={2}
                                placeholder={`תאר את הבעיה ב${sel.label}...`}
                                style={{
                                    borderRadius: 6, border: "1px solid #E5E7EB", padding: "6px 10px",
                                    fontSize: 10, resize: "none", outline: "none", background: "white", width: "100%"
                                }} />
                            <button onClick={send} className="hvr" style={{
                                background: "#DC2626", color: "white", border: "none", borderRadius: 6,
                                padding: "7px", fontSize: 11, fontWeight: 800, width: "100%", boxShadow: "0 1px 2px rgba(220,38,38,0.2)"
                            }}>שלח דיווח חדש</button>
                        </div>
                    }
                </div>
            </Panel>
        </div>
    );
}
