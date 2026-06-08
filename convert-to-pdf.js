const { mdToPdf } = require('md-to-pdf');
const path = require('path');
const fs = require('fs');

const files = [
  {
    input: path.join(__dirname, '01_Proposal_&_Analisis', 'Proposal_Teknis.md'),
    output: path.join(__dirname, '01_Proposal_&_Analisis', 'Proposal_Teknis.pdf'),
    title: 'Proposal Teknis — Sistem Lost & Found IPB',
  },
  {
    input: path.join(__dirname, '01_Proposal_&_Analisis', 'Threat_Modeling.md'),
    output: path.join(__dirname, '01_Proposal_&_Analisis', 'Threat_Modeling.pdf'),
    title: 'Threat Modeling & Vulnerability Assessment — Sistem Lost & Found IPB',
  },
  {
    input: path.join(__dirname, '04_Reports_&_Paper', 'Monitoring_P7', 'Laporan_Kemajuan_P7.md'),
    output: path.join(__dirname, '04_Reports_&_Paper', 'Monitoring_P7', 'Laporan_Kemajuan_P7.pdf'),
    title: 'Laporan Kemajuan P7 — Sistem Lost & Found IPB',
  },
];

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  * {
    box-sizing: border-box;
  }

  body {
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.7;
    color: #1a1a2e;
    margin: 0;
    padding: 0;
  }

  .page-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white;
    padding: 32px 40px;
    margin: -20mm -20mm 24px -20mm;
  }

  h1 {
    font-size: 22pt;
    font-weight: 700;
    color: #0f3460;
    margin-top: 0;
    margin-bottom: 8px;
    border-bottom: 3px solid #e94560;
    padding-bottom: 10px;
  }

  h2 {
    font-size: 15pt;
    font-weight: 600;
    color: #16213e;
    margin-top: 28px;
    margin-bottom: 10px;
    border-left: 4px solid #e94560;
    padding-left: 12px;
  }

  h3 {
    font-size: 12.5pt;
    font-weight: 600;
    color: #0f3460;
    margin-top: 20px;
    margin-bottom: 8px;
  }

  h4 {
    font-size: 11pt;
    font-weight: 600;
    color: #16213e;
    margin-top: 16px;
    margin-bottom: 6px;
  }

  p {
    margin: 8px 0 12px;
    text-align: justify;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 10pt;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  }

  thead {
    background: #0f3460;
    color: white;
  }

  thead th {
    padding: 9px 12px;
    text-align: left;
    font-weight: 600;
    font-size: 10pt;
    letter-spacing: 0.3px;
  }

  tbody tr:nth-child(even) {
    background: #f0f4ff;
  }

  tbody tr:nth-child(odd) {
    background: #ffffff;
  }

  tbody tr:hover {
    background: #e8eeff;
  }

  td {
    padding: 8px 12px;
    border: 1px solid #dde3f0;
    vertical-align: top;
    line-height: 1.5;
  }

  /* Code blocks */
  pre {
    background: #0d1117;
    color: #e6edf3;
    border-radius: 6px;
    padding: 14px 16px;
    font-family: 'JetBrains Mono', 'Consolas', 'Courier New', monospace;
    font-size: 8.5pt;
    line-height: 1.6;
    overflow-x: auto;
    margin: 12px 0;
    border-left: 3px solid #e94560;
  }

  code {
    background: #eef1f8;
    color: #0f3460;
    padding: 2px 5px;
    border-radius: 3px;
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 9pt;
  }

  pre code {
    background: none;
    color: inherit;
    padding: 0;
    font-size: inherit;
  }

  /* Lists */
  ul, ol {
    padding-left: 22px;
    margin: 8px 0 12px;
  }

  li {
    margin-bottom: 5px;
    line-height: 1.6;
  }

  li > strong:first-child {
    color: #0f3460;
  }

  /* Blockquotes */
  blockquote {
    border-left: 4px solid #e94560;
    background: #fff8f0;
    margin: 12px 0;
    padding: 10px 16px;
    color: #555;
    font-style: italic;
    border-radius: 0 6px 6px 0;
  }

  /* Horizontal rule */
  hr {
    border: none;
    border-top: 2px solid #e94560;
    margin: 24px 0;
    opacity: 0.3;
  }

  /* Strong & Em */
  strong {
    font-weight: 600;
    color: #16213e;
  }

  em {
    color: #444;
    font-style: italic;
  }

  /* Metadata block (bold key: value) */
  p > strong:first-child {
    color: #0f3460;
    min-width: 100px;
    display: inline-block;
  }

  /* Page break */
  @page {
    margin: 20mm 18mm 20mm 18mm;
    size: A4;
  }

  @media print {
    h1, h2 {
      page-break-after: avoid;
    }
    table, pre {
      page-break-inside: avoid;
    }
  }
`;

async function convert() {
  console.log('🚀 Memulai konversi Markdown → PDF...\n');

  for (const file of files) {
    if (!fs.existsSync(file.input)) {
      console.error(`❌ File tidak ditemukan: ${file.input}`);
      continue;
    }

    try {
      process.stdout.write(`📄 Mengkonversi: ${path.basename(file.input)} ...`);

      await mdToPdf(
        { path: file.input },
        {
          dest: file.output,
          css,
          pdf_options: {
            format: 'A4',
            margin: { top: '20mm', right: '18mm', bottom: '20mm', left: '18mm' },
            printBackground: true,
            displayHeaderFooter: true,
            headerTemplate: `
              <div style="font-size:8px; color:#666; width:100%; text-align:right; padding-right:18mm; font-family: Arial, sans-serif;">
                Keamanan Informasi (KOM1315) — Kelompok 2 — IPB University
              </div>
            `,
            footerTemplate: `
              <div style="font-size:8px; color:#666; width:100%; display:flex; justify-content:space-between; padding:0 18mm; font-family: Arial, sans-serif;">
                <span>${file.title}</span>
                <span>Halaman <span class="pageNumber"></span> dari <span class="totalPages"></span></span>
              </div>
            `,
          },
          launch_options: {
            args: ['--no-sandbox', '--disable-setuid-sandbox'],
          },
        }
      );

      console.log(` ✅ Selesai → ${path.basename(file.output)}`);
    } catch (err) {
      console.error(` ❌ Gagal: ${err.message}`);
    }
  }

  console.log('\n✨ Konversi selesai!');
  console.log('📁 File PDF tersimpan di:');
  files.forEach(f => console.log(`   ${f.output}`));
}

convert();
