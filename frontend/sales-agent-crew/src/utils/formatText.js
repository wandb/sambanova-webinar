export function formattedText(data) {
    // Remove any trailing JSON block starting with "```json"
    // const cleanedData = data.replace(/```json[\s\S]*$/, "").trim();
    const cleanedData = data.trim();

    const text = cleanedData || "";
    const lines = text.split("\n");
    let html = "";
    let inList = false;
    // Match bullet lines starting with *, +, or -
    const bulletRegex = /^([*+-])\s+(.*)/;
    
    lines.forEach((line) => {
      const trimmed = line.trim();
      const bulletMatch = trimmed.match(bulletRegex);
      if (bulletMatch) {
        if (!inList) {
          html += "<ul class='my-2'>";
          inList = true;
        }
        // Each bullet item gets an inline span for the bullet marker
        html += `<li class="custom-bullet"><span class="bullet-marker">•</span> ${bulletMatch[2]}</li>`;
      } else {
        if (inList) {
          html += "</ul>";
          inList = false;
        }
        if (trimmed.length > 0) {
          // If the line ends with a colon, treat it as a heading
          if (trimmed.endsWith(":")) {
            // Wrap heading text in <h2> tags
            html += `<h2 class="md-heading text-[16px] font-semibold">${trimmed}</h2>`;
          } else {
            html += `<p class="md-paragraph">${trimmed}</p>`;
          }
        }
      }
    });
    
    if (inList) {
      html += "</ul>";
    }
    
    // Replace markdown bold syntax (i.e. **text**) with HTML <strong> tags.
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    return html;
  }
  
 // utils/formatText.js

/**
 * Render the input string as formatted HTML.
 * If a JSON block (wrapped in ```json ... ```) exists, only that block is used.
 * Otherwise, if the entire content (after removing backticks) is JSON, render it as a table.
 * Otherwise, process the content as plain markdown.
 */
export function renderMarkdownWithJSON(data) {
  // Try to extract a JSON block wrapped in triple backticks.
  const jsonBlockMatch = data.match(/```json\s*([\s\S]*?)\s*```/i);
  if (jsonBlockMatch && jsonBlockMatch[1]) {
    try {
      const jsonData = JSON.parse(jsonBlockMatch[1].trim());
      return processJSON(jsonData);
    } catch (e) {
      console.error("Error parsing JSON block:", e);
      // If parsing fails, fall back to markdown processing.
      return processMarkdown(data);
    }
  }
  
  // If no JSON block is found, remove all triple backticks.
  const cleaned = data.replace(/```/g, "").trim();
  // Check if the cleaned text appears to be pure JSON.
  if (cleaned.startsWith("{") && cleaned.endsWith("}")) {
    try {
      const jsonData = JSON.parse(cleaned);
      return processJSON(jsonData);
    } catch (e) {
      console.error("Error parsing pure JSON:", e);
      return processMarkdown(data);
    }
  }
  
  // Otherwise, process as plain markdown.
  return processMarkdown(data);
}

/**
 * A basic markdown processor that wraps each nonempty line in a paragraph.
 */
function processMarkdown(data) {
  const lines = data.split("\n").filter(line => line.trim() !== "");
  let html = "";
  for (const line of lines) {
    html += `<p>${escapeHTML(line.trim())}</p>`;
  }
  return html;
}

/**
 * Renders a JSON object as an HTML table.
 * The table uses inline styles "display: inline-table; width: auto;" so that it
 * only takes up as much width as needed.
 */
function processJSON(jsonData) {
  let html = "";
  const tableStyle =
    "display: inline-table; width: auto; border-collapse: separate; border-spacing: 0; border: 1px solid #EAECF0; border-radius: 8px; margin: 1em 0; font-family: Arial, sans-serif;";
  const cellStyle = "padding: 8px; border-bottom: 1px solid #ddd;";
  const lastCellStyle = "padding: 8px;";
  
  // Helper to add a table row.
  const addRow = (key, value, isLast = false) => {
    const style = isLast ? lastCellStyle : cellStyle;
    html += `<tr>
      <td style="${cellStyle}; font-weight: bold;">${escapeHTML(key)}</td>
      <td style="${style}">${escapeHTML(String(value))}</td>
    </tr>`;
  };
  
  html += `<table style="${tableStyle}"><tbody>`;
  
  if (typeof jsonData === "object" && jsonData !== null) {
    if (Array.isArray(jsonData)) {
      // For arrays, process each element.
      jsonData.forEach((item, idx) => {
        if (typeof item === "object" && item !== null && !Array.isArray(item)) {
          Object.keys(item).forEach((key, keyIdx, arr) => {
            addRow(key, item[key], keyIdx === arr.length - 1);
          });
        } else {
          addRow(String(idx), item);
        }
      });
    } else {
      // For plain objects, process key/value pairs.
      Object.keys(jsonData).forEach(key => {
        const value = jsonData[key];
        if (typeof value === "object" && value !== null && !Array.isArray(value)) {
          // Flatten nested objects.
          Object.keys(value).forEach((innerKey, idx, arr) => {
            addRow(innerKey, value[innerKey], idx === arr.length - 1);
          });
        } else {
          addRow(key, value);
        }
      });
    }
  } else {
    html += `<tr><td colspan="2" style="${lastCellStyle}">${escapeHTML(String(jsonData))}</td></tr>`;
  }
  
  html += `</tbody></table>`;
  return html;
}

/**
 * Escapes HTML special characters to prevent XSS and rendering issues.
 */
function escapeHTML(text) {
  if (typeof text !== "string") return text;
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
