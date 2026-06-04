"""Create a realistic Apple 10-Q demo PDF for FinSight AI testing."""
import os


def make_pdf(filename: str, lines: list[str]) -> None:
    """Build a minimal but valid PDF with the given text lines."""

    def obj(n: int, body: bytes) -> bytes:
        return f"{n} 0 obj\n".encode() + body + b"\nendobj\n"

    # Page content stream
    stream_parts = ["BT", "/F1 10 Tf", "50 760 Td", "12 TL"]
    for line in lines:
        safe = line.replace("\\", "/").replace("(", "<").replace(")", ">")
        stream_parts.append(f"({safe}) Tj")
        stream_parts.append("T*")
    stream_parts.append("ET")
    stream_bytes = "\n".join(stream_parts).encode("latin-1", errors="replace")

    o1 = obj(1, b"<< /Type /Catalog /Pages 2 0 R >>")
    o2 = obj(2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    o3 = obj(
        3,
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]"
            b" /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>"
        ),
    )
    o4 = obj(4, f"<< /Length {len(stream_bytes)} >>\nstream\n".encode() + stream_bytes + b"\nendstream")
    o5 = obj(5, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    objects = [o1, o2, o3, o4, o5]

    pdf = b"%PDF-1.4\n"
    offsets = []
    for o in objects:
        offsets.append(len(pdf))
        pdf += o

    xref_pos = len(pdf)
    pdf += b"xref\n"
    pdf += f"0 {len(objects) + 1}\n".encode()
    pdf += b"0000000000 65535 f \n"
    for off in offsets:
        pdf += f"{off:010d} 00000 n \n".encode()
    pdf += b"trailer\n"
    pdf += f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode()
    pdf += b"startxref\n"
    pdf += f"{xref_pos}\n".encode()
    pdf += b"%%EOF\n"

    with open(filename, "wb") as f:
        f.write(pdf)


CONTENT = [
    "APPLE INC.",
    "FORM 10-Q",
    "For the quarterly period ended December 28, 2024",
    "",
    "UNITED STATES SECURITIES AND EXCHANGE COMMISSION",
    "Washington, D.C. 20549",
    "",
    "CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS",
    "(In millions, except per-share amounts - Unaudited)",
    "",
    "Three Months Ended December 28, 2024",
    "",
    "Net sales:",
    "  Products                                   97,963",
    "  Services                                   26,343",
    "Total net sales                             124,306",
    "",
    "Cost of sales:",
    "  Products                                   52,468",
    "  Services                                    6,468",
    "Total cost of sales                          58,936",
    "",
    "Gross margin                                 65,370",
    "",
    "Operating expenses:",
    "  Research and development                    8,268",
    "  Selling, general and administrative         6,979",
    "Total operating expenses                     15,247",
    "",
    "Operating income                             50,123",
    "Other income/(expense), net                   2,139",
    "Income before income taxes                   52,262",
    "Provision for income taxes                    6,220",
    "Net income                                   46,042",
    "",
    "Earnings per share:",
    "  Basic                                        3.05",
    "  Diluted                                      3.04",
    "",
    "YEAR-OVER-YEAR COMPARISON",
    "Q1 FY2024 Total net sales: 119,575M",
    "Q1 FY2025 Total net sales: 124,306M",
    "Revenue growth year-over-year: +3.95%",
    "",
    "SEGMENT INFORMATION",
    "Americas:              53,507  (+7.1% YoY)",
    "Europe:                29,985  (+8.1% YoY)",
    "Greater China:         18,510  (-11.1% YoY)",
    "Japan:                  7,226  (+1.2% YoY)",
    "Rest of Asia Pacific:   9,953  (+5.7% YoY)",
    "Services:              26,343  (+13.9% YoY)",
    "",
    "KEY FINANCIAL RATIOS",
    "Gross Margin:     52.6%",
    "Operating Margin: 40.3%",
    "Net Margin:       37.0%",
    "Return on Equity: 147.3%",
    "Current Ratio:     0.87",
    "",
    "CASH AND EQUIVALENTS",
    "Cash and cash equivalents:            29,943",
    "Marketable securities:                95,960",
    "Total liquidity:                     125,903",
    "",
    "GUIDANCE FOR Q2 FY2025",
    "Revenue expected between 88,500 and 91,500",
    "Gross margin between 46.5% and 47.5%",
    "Operating expenses between 15,000 and 15,200",
    "",
    "RISK FACTORS",
    "The Company faces intense competition across all product and service markets.",
    "Global supply chain constraints may impact product availability and costs.",
    "Foreign currency fluctuations materially affect international revenues.",
    "Regulatory changes across multiple jurisdictions present compliance challenges.",
    "Dependence on key third-party manufacturers, primarily located in Asia.",
    "Tariff and trade policy changes could increase component costs significantly.",
]

make_pdf("apple_10q_q1_2025.pdf", CONTENT)
size = os.path.getsize("apple_10q_q1_2025.pdf")
print(f"PDF created: apple_10q_q1_2025.pdf ({size} bytes)")
