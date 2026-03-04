import { useState, useEffect } from "react";
import { apiService } from "./api/apiService";
import { Activity } from "lucide-react";
import TopBar from "./components/layout/TopBar";
import FilterBar from "./components/layout/FilterBar";
import Sidebar from "./components/layout/Sidebar";
import GeoMap from "./components/GeoMap";
import RelMap from "./components/RelMap";

export default function App() {
    const [nodes, setNodes] = useState([]);
    const [edges, setEdges] = useState([]);
    const [sel, setSel] = useState(null);
    const [filters, setFilters] = useState({ dependency: true, alternative: true, impacts: true });
    const [typeF, setTypeF] = useState("all");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            const data = await apiService.fetchGraphData();
            setNodes(data.nodes);
            setEdges(data.edges);
            setLoading(false);
        };
        loadData();
    }, []);

    const toggleF = k => setFilters(f => ({ ...f, [k]: !f[k] }));

    const onReportIncident = async (nodeId, description) => {
        await apiService.reportIncident(nodeId, { desc: description, reporter: "User", date: new Date().toLocaleDateString("he-IL") });
        // In a real app, we would re-fetch or update local state here.
    };

    // collect all recursively impacted nodes (for chips)
    const getImpactChips = (selectedNode) => {
        if (!selectedNode) return [];
        const visited = new Set();
        const res = [];
        const dfs = id => {
            edges.filter(e => e.s === id && e.kind === "IMPACTS").forEach(e => {
                if (!visited.has(e.t)) {
                    visited.add(e.t);
                    const nd = nodes.find(n => n.id === e.t);
                    if (nd) res.push(nd);
                    dfs(e.t);
                }
            });
        };
        dfs(selectedNode.id);
        return res;
    };

    const impactChips = getImpactChips(sel);

    if (loading) {
        return (
            <div style={{ height: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#F1F5F9", fontFamily: "sans-serif" }}>
                <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: 18, fontWeight: 700, color: "#6366F1", marginBottom: 10 }}>טוען נתונים...</div>
                    <div style={{ width: 40, height: 40, border: "4px solid #E2E8F0", borderTop: "4px solid #6366F1", borderRadius: "50%", animation: "spin 1s linear infinite", margin: "0 auto" }} />
                </div>
                <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
            </div>
        );
    }

    return (
        <div dir="rtl" style={{ height: "100vh", background: "#F1F5F9", fontFamily: "'Heebo','Assistant',sans-serif", display: "flex", flexDirection: "column", overflow: "hidden" }}>
            <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600;700;800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0 }
        button { font-family: inherit; cursor: pointer }
        textarea { font-family: inherit }
        ::-webkit-scrollbar { width: 4px; height: 4px }
        ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 4px }
        .hvr { transition: all .14s }
        .hvr:hover { filter: brightness(.95) }
        .srow:hover { background: #F8FAFC }
      `}</style>

            <TopBar nodes={nodes} />
            <FilterBar
                filters={filters}
                toggleF={toggleF}
                typeF={typeF}
                setTypeF={setTypeF}
                sel={sel}
                setSel={setSel}
            />

            {/* BODY */}
            {!sel ? (
                <div style={{ flex: 1, overflow: "hidden" }}>
                    <GeoMap nodes={nodes} edges={edges} selected={null} onSelect={setSel} filters={filters} />
                </div>
            ) : (
                <div style={{ flex: 1, display: "grid", gridTemplateColumns: "1.2fr 1.2fr 2fr", overflow: "hidden" }}>
                    <Sidebar sel={sel} onReportIncident={onReportIncident} impactChips={impactChips} />
                    <div style={{ borderLeft: "1px solid #E2E8F0", overflow: "hidden", display: "flex", flexDirection: "column" }}>
                        <div style={{ padding: "10px", borderBottom: "1px solid #E2E8F0", background: "white" }}>
                            <div style={{ display: "flex", alignItems: "center", gap: 8, color: "#15803D" }}>
                                <Activity size={18} />
                                <span style={{ fontWeight: 800, fontSize: 13 }}>מפת קישורים</span>
                            </div>
                        </div>
                        <div style={{ flex: 1, overflow: "hidden" }}>
                            <RelMap sel={sel} nodes={nodes} edges={edges} />
                        </div>
                    </div>
                    <div style={{ overflow: "hidden" }}>
                        <GeoMap nodes={nodes} edges={edges} selected={sel} onSelect={setSel} filters={filters} />
                    </div>
                </div>
            )}
        </div>
    );
}
