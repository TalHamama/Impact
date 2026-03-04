export default function Panel({ children, style = {} }) {
    return (
        <div style={{
            background: "white", borderRadius: 12, border: "1px solid #E5E7EB",
            padding: "11px 13px", boxShadow: "0 1px 3px rgba(0,0,0,.05)", ...style
        }}>
            {children}
        </div>
    );
}
