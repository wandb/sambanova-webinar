<template>
    <div class="assistant-message">
      <h3>Assistant Message:</h3>
      <!-- The raw text from data.response -->
      <div v-html="formattedText"></div>
      <!-- Possibly parse the nested message if needed -->
    </div>
  </template>
  
  <script>
export default {
  props: {
    // Expecting an object with the API response, e.g., { data: { response: "..." } }
    parsed: {
      type: Object,
      required: true,
    },
  },
  computed: {
    formattedText() {
      // Extract the text from parsed.data?.response, or fallback to an empty string.
      const text = this.parsed.data?.response || '';
      const lines = text.split('\n');
      let inList = false;
      let html = '';

      // Process each line in the response
      lines.forEach((line) => {
        const trimmed = line.trim();
        // Detect lines that start with a number and a period (e.g., "1. Customization...")
        const match = trimmed.match(/^(\d+)\.\s+(.*)/);
        if (match) {
          // Start a list if not already inside one
          if (!inList) {
            html += '<ul>';
            inList = true;
          }
          // Add the list item with the custom class for colored bullet points
          html += `<li class="custom-bullet">${match[2]}</li>`;
        } else {
          // If we exit a list, close it
          if (inList) {
            html += '</ul>';
            inList = false;
          }
          // Wrap non-empty lines in paragraph tags
          if (trimmed.length > 0) {
            html += `<p>${trimmed}</p>`;
          }
        }
      });

      // Close an open list if the response ended while still in a list
      if (inList) {
        html += '</ul>';
      }

      return html;
    },
  },
};
</script>

<style scoped>
.custom-bullet {
  list-style: none; /* Remove default bullet */
  position: relative;
  padding-left: 1.25rem; /* Add space for our custom bullet */
  margin-bottom: 0.5rem;
}

.custom-bullet::before {
  content: '•';
  color: #f56565; /* Tailwind red-500 color */
  position: absolute;
  left: 0;
  top: 0;
  font-size: 1.25rem;
  line-height: 1;
}
</style>