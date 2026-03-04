export default function Ring({ score, c, size = 54 }) {
    const r = (size / 2) - 5, ci = 2 * Math.PI * r;
    return (
        <svg width={size} height={size} style={{ flexShrink: 0 }}>
            <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#F1F5F9" strokeWidth="5" />
            <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={c} strokeWidth="5"
                strokeDasharray={`${(score / 100) * ci} ${ci}`} strokeDashoffset={ci * .25} strokeLinecap="round" />
            <text x={size / 2} y={size / 2 + 5} textAnchor="middle" fontSize="13" fontWeight="800" fill={c}
                fontFamily="'Heebo',sans-serif">{score}</text>
        </svg>
    );
}
