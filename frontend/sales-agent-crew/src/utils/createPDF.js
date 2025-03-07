import { marked } from 'marked';
import DOMPurify from 'dompurify';
import html2pdf from 'html2pdf.js';
import autoTable from 'jspdf-autotable';

import { jsPDF } from 'jspdf'


export async function downloadPDF(content) {
    if (!content || !Array.isArray(content.report)) {
        console.error("Invalid content structure");
        return;
    }

    const tempDiv = document.createElement('div');
    tempDiv.style.padding = '40px';
    tempDiv.style.fontFamily = 'Arial, sans-serif';

    const styleSheet = document.createElement('style');
    styleSheet.textContent = `
      .chapter { margin-bottom: 40px; page-break-after: always; }
      .chapter:last-child { page-break-after: avoid; }
      .chapter-title { font-size: 24px; color: #1a1a1a; margin-bottom: 20px; font-weight: bold; }
      .section { margin: 15px 0; padding: 15px; border-radius: 8px; }
      .goal-section { background-color: #f0f7ff; }
      .important-section { background-color: #fff8e6; }
      .section-title { font-size: 16px; font-weight: bold; margin-bottom: 8px; }
      .content { margin-top: 20px; line-height: 1.6; }
      .content h1, .content h2, .content h3 { margin: 15px 0; color: #2c3e50; }
      .content p { margin: 10px 0; }
      .content ul, .content ol { margin: 10px 0; padding-left: 20px; }
      .content a { color: #2563eb; text-decoration: underline; }
    `;
    tempDiv.appendChild(styleSheet);

    content.report.forEach((chapter) => {
        const chapterDiv = document.createElement('div');
        chapterDiv.className = 'chapter';

        chapterDiv.innerHTML += `
          <h1 class="chapter-title">${DOMPurify.sanitize(chapter.title)}</h1>
          <div class="section goal-section">
            <div class="section-title">High Level Goal</div>
            <div>${DOMPurify.sanitize(chapter.high_level_goal)}</div>
          </div>
          <div class="section important-section">
            <div class="section-title">Why Important</div>
            <div>${DOMPurify.sanitize(chapter.why_important)}</div>
          </div>
          <div class="content">
            ${DOMPurify.sanitize(marked(chapter.generated_content || ''))}
          </div>
        `;
        tempDiv.appendChild(chapterDiv);
    });

    const opt = {
        margin: [10, 10],
        filename: 'research_report.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, letterRendering: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    try {
        await html2pdf().set(opt).from(tempDiv).save();
    } catch (error) {
        console.error('Error generating PDF:', error);
        alert("Failed to generate PDF. Please try again.");
    }
}




export async function generatePDFDeepResearch(data, headerConfig) {
    console.log("Received data:", data);
    
    // Validate input and extract final_report
    const finalReport = data.final_report || data?.data?.final_report;
    if (!finalReport || typeof finalReport !== 'string') {
      console.error("Error: No 'final_report' found.");
      alert("No research report available to generate PDF.");
      return;
    }
    console.log("Final Report Extracted:", finalReport);
  
    // Initialize jsPDF
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });
    
    let yPosition = 20;
    const pageHeight = pdf.internal.pageSize.height - 20;
    
    // --- Header ---
    pdf.setFont('helvetica', 'bold');
    pdf.setFontSize(24);
    pdf.setTextColor(33, 37, 41); // dark gray
    pdf.text(headerConfig.topHeading || 'Research Report', 15, yPosition);
    yPosition += 12;
    
    pdf.setFont('helvetica', 'italic');
    pdf.setFontSize(16);
    pdf.setTextColor(100, 100, 100); // lighter gray
    pdf.text(headerConfig.subHeading || 'Generated with Vue 3', 15, yPosition);
    yPosition += 12;
    
    // --- Convert Markdown to HTML and then to plain text ---
    // Use marked and DOMPurify to generate sanitized HTML
    let markdownHTML = DOMPurify.sanitize(marked(finalReport, { breaks: true }));
    // Split the HTML into lines (this is a simple approach; adjust as needed)
    const htmlLines = markdownHTML.split('\n');
    
    // Set default text style
    pdf.setFont('helvetica', 'normal');
    pdf.setFontSize(12);
    pdf.setTextColor(33, 37, 41);
    
    // Process each line and adjust styling based on detected HTML tags
    htmlLines.forEach((line) => {
      let cleanLine = line.trim();
      
      // Detect headings (using simple regex on the generated HTML)
      if (/<h1>(.*?)<\/h1>/.test(cleanLine)) {
        const text = cleanLine.replace(/<\/?h1>/g, "");
        pdf.setFont('helvetica', 'bold');
        pdf.setFontSize(18);
        pdf.text(text, 15, yPosition);
        yPosition += 10;
      } else if (/<h2>(.*?)<\/h2>/.test(cleanLine)) {
        const text = cleanLine.replace(/<\/?h2>/g, "");
        pdf.setFont('helvetica', 'bold');
        pdf.setFontSize(16);
        pdf.text(text, 15, yPosition);
        yPosition += 8;
      } else if (/<h3>(.*?)<\/h3>/.test(cleanLine)) {
        const text = cleanLine.replace(/<\/?h3>/g, "");
        pdf.setFont('helvetica', 'bold');
        pdf.setFontSize(14);
        pdf.text(text, 15, yPosition);
        yPosition += 7;
      }
      // Detect bullet list items
      else if (/<li>(.*?)<\/li>/.test(cleanLine)) {
        const text = cleanLine.replace(/<\/?li>/g, "");
        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(12);
        pdf.text("• " + text, 20, yPosition);
        yPosition += 6;
      }
      // Detect table rows (we assume tables have been converted to plain text here)
      else if (/<table>/i.test(cleanLine)) {
        // Skip, autoTable will handle tables if you decide to re-process HTML tables separately.
      }
      // Otherwise treat as paragraph
      else if (/<p>(.*?)<\/p>/.test(cleanLine)) {
        const text = cleanLine.replace(/<\/?p>/g, "");
        const wrappedText = pdf.splitTextToSize(text, 180);
        wrappedText.forEach((wLine) => {
          pdf.text(wLine, 15, yPosition);
          yPosition += 7;
          if (yPosition > pageHeight) {
            pdf.addPage();
            yPosition = 20;
          }
        });
        yPosition += 3; // extra space after paragraph
      }
      // If no known tag, just add the text
      else if (cleanLine.length > 0) {
        const wrappedText = pdf.splitTextToSize(cleanLine, 180);
        wrappedText.forEach((wLine) => {
          pdf.text(wLine, 15, yPosition);
          yPosition += 7;
          if (yPosition > pageHeight) {
            pdf.addPage();
            yPosition = 20;
          }
        });
      }
      
      // Add a page break if near the end of the page
      if (yPosition > pageHeight) {
        pdf.addPage();
        yPosition = 20;
      }
    });
    
    // --- Page Numbers ---
    for (let i = 1; i <= pdf.internal.getNumberOfPages(); i++) {
      pdf.setPage(i);
      pdf.setFontSize(10);
      pdf.setTextColor(150, 150, 150);
      pdf.text(`Page ${i}`, pdf.internal.pageSize.width - 25, pdf.internal.pageSize.height - 10);
    }
    
    // --- Citations ---
    const citationsMatch = finalReport.match(/(^|\n)##\s*Citations\s*(\n|$)/i);
    let citationData = [];
    if (citationsMatch) {
      pdf.addPage();
      yPosition = 20;
      pdf.setFont('helvetica', 'bold');
      pdf.setFontSize(16);
      pdf.setTextColor(33, 37, 41);
      pdf.text("Sources & Citations", 15, yPosition);
      yPosition += 10;
    
      const citationLines = finalReport.split("\n").filter(line => line.startsWith("* ") || line.startsWith("- "));
    
      citationData = citationLines.map(citation => {
        // Try to capture Markdown link syntax
        let match = citation.match(/\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/);
        if (match) {
          return [match[1], match[2]];
        }
        // Fallback: show the raw citation text
        return [citation.replace("* ", "").replace("- ", ""), ""];
      });
    
      if (citationData.length > 0) {
        // Use autoTable for neat citation formatting
        autoTable(pdf, {
          head: [['Title', 'URL']],
          body: citationData,
          startY: yPosition,
          theme: 'grid',
          styles: { fontSize: 10, cellPadding: 3, halign: 'left' },
          columnStyles: { 1: { cellWidth: 90 } },
          didDrawCell: function (data) {
            // Ensure the URL cell displays as clickable link
            if (data.column.index === 1 && citationData[data.row.index] && citationData[data.row.index][1]) {
              pdf.setTextColor(0, 0, 255);
              pdf.textWithLink(citationData[data.row.index][1], data.cell.x + 2, data.cell.y + 5, {
                url: citationData[data.row.index][1]
              });
              pdf.setTextColor(0, 0, 0);
            }
          }
        });
      } else {
        pdf.setFontSize(12);
        pdf.text("No valid citations found.", 15, yPosition);
      }
    }
    
    // --- Save PDF ---
    pdf.save('chatgpt_research_styled.pdf');
  }

