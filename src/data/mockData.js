import { CheckCircle, AlertTriangle, XCircle } from "lucide-react";

export const NODES = [
    // --- ZONES: Tel Aviv & Surroundings ---
    {
        id: "n1", label: "רמת גן א", short: "רמת גן א", type: "A", onMap: true, status: "active", score: 85, lat: 32.082, lng: 34.811, effortColor: null,
        description: "NODE ראשי של אזור רמת גן. תלוי בתחנה א, משפיע על משימה א ומשימה ב.",
        coords: "32.08°N, 34.81°E", zone: "רמת גן", owner: "עיריית רמת גן",
        impacts: ["משימה א", "משימה ב"], alternatives: ["רמת גן ב"],
        incidents: [{ date: "01/03/2026", reporter: "דנה כהן", desc: "עיכוב קל בהעברת משאבים למשימה א.", status: "בטיפול" }],
        steps: ["בדוק קישוריות מול תחנה א", "אם תחנה א אינה זמינה — עבור לתחנה ב דרך רמת גן ב", "הפעל נוהל חלופי דרך רמת גן ב", "עדכן מנהל אזור על המעבר לחלופה"],
    },
    {
        id: "n9", label: "גבעתיים א", short: "גבעתיים א", type: "A", onMap: true, status: "active", score: 88, lat: 32.072, lng: 34.812, effortColor: null,
        description: "NODE של אזור גבעתיים. תלוי בתחנה א, מושפע ומשפיע על משימה א.",
        coords: "32.07°N, 34.81°E", zone: "גבעתיים", owner: "עיריית גבעתיים",
        impacts: ["משימה א"], alternatives: [],
        incidents: [],
        steps: ["בדוק קישוריות מול תחנה א", "אם תחנה א לא זמינה — פנה לגורם מאשר להפעלת חלופה", "עדכן מנהל אזור"],
    },
    {
        id: "n5", label: "רמת גן ב", short: "רמת גן ב", type: "A", onMap: true, status: "active", score: 90, lat: 32.101, lng: 34.842, effortColor: null,
        description: "NODE חלופי לרמת גן א. מופעל כאשר רמת גן א אינו זמין. תלוי בתחנה ב.",
        coords: "32.10°N, 34.84°E", zone: "רמת גן", owner: "עיריית רמת גן",
        impacts: [], alternatives: [],
        incidents: [],
        steps: ["וודא שתחנה ב פעילה לפני הפעלת החלופה", "הפעל נוהל מעבר מרמת גן א", "עדכן את כלל ה-NODEs המושפעים"],
    },
    {
        id: "n17", label: "תל אביב מרכז", short: "ת״א מרכז", type: "A", onMap: true, status: "active", score: 94, lat: 32.075, lng: 34.785, effortColor: null,
        description: "מרכז תפעולי גוש דן. קריטי לניהול תנועה ותשתיות עירוניות.",
        coords: "32.07°N, 34.78°E", zone: "תל אביב", owner: "עיריית תל אביב",
        impacts: ["משימה ד"], alternatives: ["תל אביב צפון"],
        incidents: [],
        steps: ["ניטור עומסי תנועה", "תיאום מול מוקד 106"],
    },
    {
        id: "n18", label: "תל אביב צפון", short: "ת״א צפון", type: "A", onMap: true, status: "active", score: 91, lat: 32.115, lng: 34.805, effortColor: null,
        description: "שלוחה צפונית של מרכז התפעול. גיבוי למרכז העיר.",
        coords: "32.11°N, 34.80°E", zone: "תל אביב", owner: "עיריית תל אביב",
        impacts: [], alternatives: [],
        incidents: [],
        steps: ["בדיקת תקינות מערכות קשר"],
    },

    // --- ZONES: Holon, Bat Yam, Rishon ---
    {
        id: "n12", label: "חולון מרכז", short: "חולון", type: "A", onMap: true, status: "active", score: 82, lat: 32.015, lng: 34.773, effortColor: null,
        description: "מרכז בקרה לעיר חולון. מזין משימות לוגיסטיקה בדרום גוש דן.",
        coords: "32.01°N, 34.77°E", zone: "חולון", owner: "עיריית חולון",
        impacts: ["משימה ג"], alternatives: ["בת ים א"],
        incidents: [],
        steps: ["בדוק הספקת חשמל מקומית", "תאם עם תחנה ג"],
    },
    {
        id: "n13", label: "בת ים א", short: "בת ים", type: "A", onMap: true, status: "warning", score: 61, lat: 32.021, lng: 34.755, effortColor: null,
        description: "אתר גיבוי חופי. תקלות תקשורת קלות דווחו לאחרונה.",
        coords: "32.02°N, 34.75°E", zone: "בת ים", owner: "עיריית בת ים",
        impacts: ["משימה ג"], alternatives: [],
        incidents: [{ date: "04/03/2026", reporter: "קובי רז", desc: "חשש לשיבושי GPS סמוך לקו החוף.", status: "בטיפול" }],
        steps: ["עבור לניווט לא מבוסס GPS", "דווח לחמ״ל חוף"],
    },
    {
        id: "n19", label: "ראשון לציון מערב", short: "ראשל״צ מע׳", type: "A", onMap: true, status: "active", score: 87, lat: 31.975, lng: 34.765, effortColor: null,
        description: "מרכז לוגיסטי פלמחים. תלוי בתחנה ג.",
        coords: "31.97°N, 34.76°E", zone: "ראשל״צ", owner: "עיריית ראשל״צ",
        impacts: ["משימה ה"], alternatives: [],
        incidents: [],
        steps: ["תיאום מול בסיס פלמחים"],
    },

    // --- ZONES: Petah Tikva & Bnei Brak ---
    {
        id: "n20", label: "פתח תקווה צפון", short: "פ״ת צפון", type: "A", onMap: true, status: "active", score: 84, lat: 32.105, lng: 34.885, effortColor: null,
        description: "אזור תעשייה סגולה. מרכז לוגיסטי לאספקה מזרחית.",
        coords: "32.10°N, 34.88°E", zone: "פתח תקווה", owner: "עיריית פתח תקווה",
        impacts: ["משימה ו"], alternatives: ["בני ברק מזרח"],
        incidents: [],
        steps: ["בדיקת מלאי חירום"],
    },
    {
        id: "n21", label: "בני ברק מזרח", short: "ב״ב מזרח", type: "A", onMap: true, status: "active", score: 89, lat: 32.085, lng: 34.845, effortColor: null,
        description: "NODE עזר לאזור התעסוקה בני ברק.",
        coords: "32.08°N, 34.84°E", zone: "בני ברק", owner: "עיריית בני ברק",
        impacts: ["משימה ו"], alternatives: [],
        incidents: [],
        steps: ["תיאום מול פיקוד העורף"],
    },

    // --- STATIONS (Type B) ---
    {
        id: "n2", label: "תחנה א", short: "תחנה א", type: "B", onMap: true, status: "active", score: 92, lat: 32.091, lng: 34.792, effortColor: null,
        description: "תחנת מקור ראשית המזינה את NODE רמת גן א ו-NODE גבעתיים א.",
        coords: "32.09°N, 34.79°E", zone: "תל אביב", owner: "רשות התשתיות",
        impacts: ["רמת גן א", "גבעתיים א"], alternatives: [],
        incidents: [],
        steps: ["פנה לצוות טכני של רשות התשתיות", "הפעל מחולל גיבוי פנימי", "עדכן NODEs תלויים"],
    },
    {
        id: "n6", label: "תחנה ב", short: "תחנה ב", type: "B", onMap: true, status: "active", score: 95, lat: 32.122, lng: 34.821, effortColor: null,
        description: "תחנת מקור גיבוי המזינה את NODE רמת גן ב.",
        coords: "32.12°N, 34.82°E", zone: "תל אביב", owner: "רשות התשתיות",
        impacts: ["רמת גן ב"], alternatives: [],
        incidents: [],
        steps: ["פנה לצוות טכני של רשות התשתיות", "וודא הפעלה תקינה של מחולל הגיבוי"],
    },
    {
        id: "n14", label: "תחנה ג", short: "תחנה ג", type: "B", onMap: true, status: "active", score: 89, lat: 31.981, lng: 34.802, effortColor: null,
        description: "תחנת כוח דרומית המזינה את חולון ובת ים.",
        coords: "31.98°N, 34.80°E", zone: "ראשל״צ", owner: "חברת חשמל",
        impacts: ["חולון מרכז", "ראשון לציון מערב"], alternatives: [],
        incidents: [],
        steps: ["בדוק עומסים בקו 400", "תאם עם תחנת חולון"],
    },
    {
        id: "n22", label: "תחנה ד - רידינג", short: "רידינג", type: "B", onMap: true, status: "failed", score: 12, lat: 32.105, lng: 34.775, effortColor: null,
        description: "תחנה צפונית ת\"א. תקלה קריטית במחוללי הטורבינה.",
        coords: "32.10°N, 34.77°E", zone: "תל אביב", owner: "חברת חשמל",
        impacts: ["תל אביב מרכז", "תל אביב צפון"], alternatives: ["תחנה א"],
        incidents: [{ date: "04/03/2026", reporter: "משה דיין", desc: "שריפה במערך הטרנספורמטורים. השבתה מלאה.", status: "בטיפול" }],
        steps: ["כיבוי אש מיידי", "ניתוק מתח גבוה", "דיווח למשרד האנרגיה"],
    },
    {
        id: "n23", label: "מרכז תקשורת א", short: "תקשורת א", type: "B", onMap: true, status: "warning", score: 48, lat: 32.065, lng: 34.855, effortColor: null,
        description: "מוקד סיבים אופטיים ראשי לאזור המזרח.",
        coords: "32.06°N, 34.85°E", zone: "פתח תקווה", owner: "בזק",
        impacts: ["פתח תקווה צפון", "בני ברק מזרח"], alternatives: [],
        incidents: [{ date: "04/03/2026", reporter: "אריאל שרון", desc: "מתקפת סייבר מונעת שירות (DDoS).", status: "בטיפול" }],
        steps: ["הפעלת חומת אש חלופית", "תיאום מול מערך הסייבר הלאומי"],
    },

    // --- MISSIONS (Type A - but OffMap) ---
    {
        id: "n3", label: "משימה א", short: "משימה א", type: "A", onMap: false, status: "active", score: 78, lat: 32.061, lng: 34.781, effortColor: null,
        description: "משימה תפעולית הנשענת על רמת גן א. כשל ישפיע על מאמץ החשמל.",
        coords: "32.06°N, 34.78°E", zone: "רמת גן", owner: "מפקד אזור",
        impacts: ["מאמץ החשמל", "גבעתיים א"], alternatives: [],
        incidents: [],
        steps: ["בדוק זמינות משאבי כוח האדם", "אתר מקור חלופי", "דווח למפקד אזור על עיכוב"],
    },
    {
        id: "n4", label: "משימה ב", short: "משימה ב", type: "A", onMap: false, status: "warning", score: 55, lat: 32.071, lng: 34.832, effortColor: null,
        description: "משימה תפעולית שנייה הנשענת על רמת גן א. כשל ישפיע על מאמץ המים ומאמץ האוכל.",
        coords: "32.07°N, 34.83°E", zone: "רמת גן", owner: "מפקד אזור",
        impacts: ["מאמץ המים", "מאמץ האוכל"], alternatives: [],
        incidents: [{ date: "02/03/2026", reporter: "אבי לוי", desc: "ירידה בקצב ביצוע המשימה, 55% תפוקה.", status: "בטיפול" }],
        steps: ["בדוק מצב שרשרת האספקה", "הפעל צוות חלופי אם זמין", "תעד את הפגיעה ועדכן מפקד"],
    },
    {
        id: "n15", label: "משימה ג", short: "משימה ג", type: "A", onMap: false, status: "active", score: 91, lat: 31.99, lng: 34.78, effortColor: null,
        description: "לוגיסטיקה ושינוע ציוד רפואי בדרום גוש דן.",
        coords: "—", zone: "חולון", owner: "מפקד לוגיסטיקה",
        impacts: ["מאמץ הרפואה"], alternatives: [],
        incidents: [],
        steps: ["תאם מסלול מול בת ים", "וודא זמינות רכבי קירור"],
    },
    {
        id: "n24", label: "משימה ד", short: "משימה ד", type: "A", onMap: false, status: "active", score: 86, lat: 32.05, lng: 34.78, effortColor: null,
        description: "ניהול תנועה חכם במרכז תל אביב.",
        coords: "—", zone: "תל אביב", owner: "אגף התנועה",
        impacts: ["מאמץ האנשים"], alternatives: [],
        incidents: [],
        steps: ["עדכון Waze", "הפעלת רמזורים ידנית"],
    },
    {
        id: "n25", label: "משימה ה", short: "משימה ה", type: "A", onMap: false, status: "active", score: 82, lat: 31.96, lng: 34.75, effortColor: null,
        description: "אספקת דלק לחולון וראשל״צ.",
        coords: "—", zone: "ראשל״צ", owner: "תש״ן",
        impacts: ["מאמץ החשמל"], alternatives: [],
        incidents: [],
        steps: ["בדיקת לחצים בצינור"],
    },
    {
        id: "n26", label: "משימה ו", short: "משימה ו", type: "A", onMap: false, status: "warning", score: 42, lat: 32.1, lng: 34.85, effortColor: null,
        description: "אבטחת תקשורת מזרחית.",
        coords: "—", zone: "פתח תקווה", owner: "תקשוב",
        impacts: ["מאמץ האנשים", "מאמץ האוכל"], alternatives: [],
        incidents: [{ date: "04/03/2026", reporter: "יונס", desc: "שיבושי קליטה קשים.", status: "בטיפול" }],
        steps: ["חיבור לגיבוי לווייני"],
    },

    // --- EFFORTS (Type C) ---
    {
        id: "n7", label: "מאמץ האנשים", short: "אנשים", type: "C", onMap: false, status: "active", score: 80, lat: 0, lng: 0, effortColor: "#7C3AED",
        description: "מאמץ כוח האדם.",
        coords: "—", zone: "שטח מבצעי", owner: "מפקד שטח",
        impacts: [], alternatives: [],
        incidents: [],
        steps: ["הפנה כוח אדם ממשימות עדיפות נמוכה", "דווח למפקד על מצב הכוח"],
    },
    {
        id: "n8", label: "מאמץ האוכל", short: "אוכל", type: "C", onMap: false, status: "warning", score: 50, lat: 0, lng: 0, effortColor: "#0891B2",
        description: "מאמץ אספקת המזון הנשען על משימה ב.",
        coords: "—", zone: "שטח מבצעי", owner: "מפקד שטח",
        impacts: [], alternatives: [],
        incidents: [{ date: "02/03/2026", reporter: "רונית שמיר", desc: "עיכוב באספקת מזון בשל תקלה במשימה ב.", status: "בטיפול" }],
        steps: ["הפעל מלאי חירום", "אתר מסלול אספקה חלופי", "עדכן מפקד שטח בדחיפות"],
    },
    {
        id: "n10", label: "מאמץ המים", short: "מים", type: "C", onMap: false, status: "active", score: 73, lat: 0, lng: 0, effortColor: "#0EA5E9",
        description: "מאמץ אספקת המים הנשען על משימה ב.",
        coords: "—", zone: "שטח מבצעי", owner: "מפקד שטח",
        impacts: [], alternatives: [],
        incidents: [],
        steps: ["הפעל מאגר חירום", "עדכן מפקד על מצב אספקת המים"],
    },
    {
        id: "n11", label: "מאמץ החשמל", short: "חשמל", type: "C", onMap: false, status: "active", score: 82, lat: 0, lng: 0, effortColor: "#D97706",
        description: "מאמץ אספקת החשמל הנשען על משימה א.",
        coords: "—", zone: "שטח מבצעי", owner: "מפקד שטח",
        impacts: [], alternatives: [],
        incidents: [],
        steps: ["הפעל גנרטור גיבוי", "בדוק עומסים על הרשת", "דווח למפקד"],
    },
    {
        id: "n16", label: "מאמץ הרפואה", short: "רפואה", type: "C", onMap: false, status: "active", score: 94, lat: 0, lng: 0, effortColor: "#E11D48",
        description: "שירותי רפואת חירום ופינוי.",
        coords: "—", zone: "גוש דן", owner: "משרד הבריאות",
        impacts: [], alternatives: [],
        incidents: [],
        steps: ["תעדוף קריאות דחופות", "וודא עתודות דם"],
    },
    {
        id: "n27", label: "מאמץ החילוץ", short: "חילוץ", type: "C", onMap: false, status: "active", score: 98, lat: 0, lng: 0, effortColor: "#F43F5E",
        description: "יחידות חילוץ והצלה והגנה אזרחית.",
        coords: "—", zone: "ארצי", owner: "פקע״ר",
        impacts: [], alternatives: [],
        incidents: [],
        steps: ["כוננות שיא", "בדיקת ציוד הנדסי"],
    },
];

export const EDGES = [
    // --- Dependencies ---
    { id: "e1", s: "n2", t: "n1", kind: "DEPENDENCY" },   // תחנה א → רמת גן א
    { id: "e6", s: "n2", t: "n9", kind: "DEPENDENCY" },   // תחנה א → גבעתיים א
    { id: "e5", s: "n6", t: "n5", kind: "DEPENDENCY" },   // תחנה ב → רמת גן ב
    { id: "e12", s: "n14", t: "n12", kind: "DEPENDENCY" },   // תחנה ג → חולון
    { id: "e13", s: "n14", t: "n13", kind: "DEPENDENCY" },   // תחנה ג → בת ים
    { id: "e19", s: "n14", t: "n19", kind: "DEPENDENCY" },   // תחנה ג → ראשל״צ מע׳
    { id: "e20", s: "n22", t: "n17", kind: "DEPENDENCY" },   // רידינג → ת״א מרכז
    { id: "e21", s: "n22", t: "n18", kind: "DEPENDENCY" },   // רידינג → ת״א צפון
    { id: "e22", s: "n23", t: "n20", kind: "DEPENDENCY" },   // תקשורת א → פ״ת צפון
    { id: "e23", s: "n23", t: "n21", kind: "DEPENDENCY" },   // תקשורת א → ב״ב מזרח

    // --- Impacts ---
    { id: "e2", s: "n1", t: "n3", kind: "IMPACTS" },      // רמת גן א → משימה א
    { id: "e3", s: "n1", t: "n4", kind: "IMPACTS" },      // רמת גן א → משימה ב
    { id: "e14", s: "n12", t: "n15", kind: "IMPACTS" },     // חולון → משימה ג
    { id: "e15", s: "n13", t: "n15", kind: "IMPACTS" },     // בת ים → משימה ג
    { id: "e24", s: "n17", t: "n24", kind: "IMPACTS" },     // ת״א מרכז → משימה ד
    { id: "e25", s: "n19", t: "n25", kind: "IMPACTS" },     // ראשל״צ מע׳ → משימה ה
    { id: "e26", s: "n20", t: "n26", kind: "IMPACTS" },     // פ״ת צפון → משימה ו
    { id: "e27", s: "n21", t: "n26", kind: "IMPACTS" },     // ב״ב מזרח → משימה ו

    // --- Mission Impacts ---
    { id: "e7", s: "n3", t: "n11", kind: "IMPACTS" },      // משימה א → מאמץ החשמל
    { id: "e8", s: "n4", t: "n10", kind: "IMPACTS" },      // משימה ב → מאמץ המים
    { id: "e9", s: "n4", t: "n8", kind: "IMPACTS" },      // משימה ב → מאמץ האוכל
    { id: "e16", s: "n15", t: "n16", kind: "IMPACTS" },     // משימה ג → מאמץ הרפואה
    { id: "e28", s: "n24", t: "n7", kind: "IMPACTS" },      // משימה ד → מאמץ האנשים
    { id: "e29", s: "n25", t: "n11", kind: "IMPACTS" },     // משימה ה → מאמץ החשמל
    { id: "e30", s: "n26", t: "n7", kind: "IMPACTS" },      // משימה ו → מאמץ האנשים
    { id: "e31", s: "n26", t: "n8", kind: "IMPACTS" },      // משימה ו → מאמץ האוכל
    { id: "e32", s: "n25", t: "n27", kind: "IMPACTS" },     // משימה ה → מאמץ החילוץ

    // --- Alternatives ---
    { id: "e4", s: "n1", t: "n5", kind: "ALTERNATIVE" },  // רמת גן א ↔ רמת גן ב
    { id: "e17", s: "n12", t: "n13", kind: "ALTERNATIVE" }, // חולון ↔ בת ים
    { id: "e33", s: "n17", t: "n18", kind: "ALTERNATIVE" }, // ת״א מרכז ↔ ת״א צפון
    { id: "e34", s: "n20", t: "n21", kind: "ALTERNATIVE" }, // פ״ת צפון ↔ ב״ב מזרח
    { id: "e35", s: "n22", t: "n2", kind: "ALTERNATIVE" },  // רידינג ↔ תחנה א

    // --- Cross Connections ---
    { id: "e10", s: "n3", t: "n9", kind: "IMPACTS" },      // משימה א → גבעתיים א
    { id: "e11", s: "n9", t: "n3", kind: "IMPACTS" },      // גבעתיים א → משימה א
    { id: "e18", s: "n9", t: "n7", kind: "IMPACTS" },      // גבעתיים א → מאמץ האנשים
    { id: "e36", s: "n17", t: "n1", kind: "IMPACTS" },      // ת״א מרכז → רמת גן א
];

export const ST = {
    active: { label: "תקין", c: "#15803D", bg: "#F0FDF4", bd: "#86EFAC", dot: "#22C55E", Icon: CheckCircle },
    warning: { label: "תקלה", c: "#B45309", bg: "#FFFBEB", bd: "#FCD34D", dot: "#F59E0B", Icon: AlertTriangle },
    failed: { label: "כשל", c: "#DC2626", bg: "#FEF2F2", bd: "#FECACA", dot: "#EF4444", Icon: XCircle },
};

export const ECFG = {
    DEPENDENCY: { color: "#6366F1", dash: "none", label: "תלות", w: 2.2 },
    ALTERNATIVE: { color: "#F59E0B", dash: "7,4", label: "חלופה", w: 2.0 },
    IMPACTS: { color: "#EF4444", dash: "4,3", label: "השפעה", w: 1.8 },
};
