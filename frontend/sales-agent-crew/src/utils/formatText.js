export function formattedText(data) {
    // Remove any trailing JSON block starting with "```json"
    const cleanedData = data.replace(/```json[\s\S]*$/, "").trim();
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
  