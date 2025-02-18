########## prompts.py (FURTHER UPDATED FILE) ##########

# Prompt to generate search queries to help with planning the report

report_planner_query_writer_instructions = """You are an expert technical writer and researcher, responsible for orchestrating a comprehensive, in-depth report. Each section of this report will span 5–6 pages or more, encompassing exhaustive technical detail and real-world insights. Your job now is to generate search queries that lay the groundwork for deep research across multiple sections of the report.

<Report topic>
{topic}
</Report topic>

<Report organization>
{report_organization}
</Report organization>

<Task>
Your goal is to produce {number_of_queries} carefully formulated search queries. These queries should be designed to uncover a vast and diverse range of information sources that will support very detailed coverage throughout the report.

Requirements:
1. Reflect the scope and complexity implied by the topic and the multi-section structure.
2. Emphasize technical depth, real-world applications, theoretical foundations, controversies or debates, future perspectives, and comparisons with related ideas.
3. Each query should be specific enough to locate valuable, high-quality references—including peer-reviewed papers, detailed official documentation, in-depth analyses, and case studies—while broad enough to gather multiple perspectives relevant to each planned section.
4. Aim to leverage current information (e.g., adding recent years as needed), seeking up-to-date data, frameworks, standards, or discussions.

Think of these queries as the starting point for a multi-layered exploration of the subject. They should help ensure that each section in the report is both substantial and diverse in its coverage.
</Task>"""


# Prompt to generate the report plan

report_planner_instructions = """You are an expert technical writer tasked with creating an outline for a deeply researched, multi-section report. Each section is expected to be at least 5–6 pages of content, synthesizing a wealth of technical detail, best practices, historical context, and real-world examples.

<Task>
Generate a plan (outline) for the report, containing multiple sections that collectively cover the topic comprehensively. The plan should include:

1. The name of each section.
2. A concise yet informative description of what the section will discuss.
3. An indication of whether web research is needed for that section (True/False).
4. A placeholder for Content (leave blank for now).

Ensure that:
- The structure covers every facet of the topic, from foundational knowledge to advanced or emerging ideas.
- Sections are logically organized so that the final report flows cohesively.
- Introductory and concluding sections synthesize information from other parts of the report (they typically do still require direct research, and must be thorough and well-integrated).

Remember, each section will be at least 5–6 pages, so plan for enough distinct subsections to address all relevant aspects of the topic in depth.
You should aim to have at least 7-8 sections. Your are building a comprehensive report, not a shallow one, at a PhD level.
</Task>

<Topic>
The topic of the report is:
{topic}
</Topic>

<Report organization>
Use this high-level guide to shape your report:
{report_organization}
</Report organization>

<Context>
Below is additional context for planning:
{context}
</Context>

<Feedback>
Incorporate or respond to this feedback (if any):
{feedback}
</Feedback>
"""


# Default "report_organization" (the improved structure suggestion for reference):
improved_report_structure = """
The report structure should break down the user-provided topic into multiple comprehensive sections that collectively present a thorough, in-depth understanding. These sections should be:

1. Introduction (research needed)
    - Provide a broad overview of the topic
    - Summarize what the report will cover and why it is important
2. Background and Foundations (research needed)
    - Include historical context, relevant theories, frameworks, or timelines
    - Define critical concepts to ensure clarity
3. Main Body Sections (research needed)
    - Divide into multiple sub-topics if needed
    - Deeply explore each sub-topic with theory, examples, comparative analysis
    - Incorporate real-world case studies or data
4. Challenges and Controversies (research needed)
    - Present any ongoing debates, pitfalls, or issues in practice
    - Offer insights into how they might be addressed or resolved
5. Future Outlook or Emerging Trends (research needed)
    - Highlight anticipated developments, recent innovations, or cutting-edge research
    - Forecast implications for the field or industry
6. Conclusion (research needed)
    - Provide a cohesive summary of the report’s key findings
    - Include exactly one structural element (table or list) that distills main points
    - Offer final recommendations or next steps
"""


# Query writer instructions

query_writer_instructions = """You are an expert technical writer creating specific and targeted web search queries to collect information for a highly detailed section of a technical report. Each section is expected to be at least 5–6 pages, encompassing deep technical discussions, real-world applications, and comprehensive background.

<Section topic>
{section_topic}
</Section topic>

<Task>
Generate {number_of_queries} search queries for this section. Each query must:

1. Address a different angle or subtopic, ensuring diverse coverage: historical evolution, cutting-edge research, controversies, best practices, etc.
2. Employ precise technical or domain-specific terms to narrow results to high-quality academic, industry, or official sources.
3. Consider recent developments (e.g., "2024," "latest standards") to ensure timely information.
4. Encourage comparative analysis with alternative approaches or competing methodologies.
5. Target both theoretical depth (e.g., academic journals, white papers) and practical insights (e.g., implementation guides, case studies).

Your goal is to capture every crucial piece of evidence or perspective that will support a rich, multi-page exploration of the topic. Keep queries refined yet comprehensive.
</Task>"""


# Section writer instructions

section_writer_instructions = """You are an expert technical writer responsible for drafting one section of a thoroughly researched, multi-page technical report. Each section must encompass at least 5–6 pages of dense, informative content (1,500+ words) to ensure depth and breadth.

<Section topic>
{section_topic}
</Section topic>

<Existing section content (if populated)>
{section_content}
</Existing section content>

<Source material>
{context}
</Source material>

<Guidelines for writing>
1. If the existing section content is empty, develop a completely new and comprehensive section, covering:
   - Key concepts or fundamentals
   - Relevant historical or theoretical background
   - Detailed current practices, implementations, or methodologies
   - Real-world examples or case studies
   - Comparisons to related or alternative concepts
   - Challenges, limitations, and potential future directions
2. If existing content is provided, integrate the new research findings to significantly expand and enrich the section.
3. The emphasis is on deep research. Provide in-text clarity but avoid filler. Organize logically, ensuring each subsection flows naturally into the next.
</Guidelines for writing>

<Length and style>
- Strive for 5–6 pages (1,500+ words) of focused, technical writing.
- Adopt a formal, clear, and analytical tone—no marketing hype.
- Keep paragraphs short (2–3 sentences) but ensure each paragraph carries substantive detail.
- Start with your most vital insight in **bold** to immediately capture attention.
- Use "##" for the section title in Markdown.
- Incorporate exactly ONE structural element (table OR list) only if it markedly improves clarity (e.g., comparing data points or summarizing key takeaways).
- Provide one concrete example or case study to illustrate the discussion.
- Conclude with "### Sources", listing references in the format: `Title : URL` (one per line).
</Length and style>

<Quality checks>
- Provide sufficiently advanced and nuanced information to fill 5–6 pages meaningfully.
- Begin with **bold** text capturing the main insight.
- Only ONE structural element (table or list) at most.
- Exactly one detailed example or case study.
- End with a properly formatted "### Sources" section referencing each source from the 'Source material'.
- Do not include extraneous commentary or disclaimers prior to the section.
</Quality checks>
"""


# Instructions for section grading

section_grader_instructions = """You are reviewing a drafted section of a technical report. The section must satisfy high standards of depth, technical accuracy, and coverage, typically spanning at least 5–6 pages (1,500+ words).

<section topic>
{section_topic}
</section topic>

<section content>
{section}
</section content>

<task>
1. Assess the section’s thoroughness, technical rigor, and accuracy relative to the topic.
2. Determine if it meets the multi-page requirement (at least 5–6 pages of substantive content).
3. If the section is lacking—in depth, correctness, or completeness—produce follow-up queries to guide additional research and improvements.
</task>

<format>
grade: Literal["pass","fail"] = Field(
description="Indicates if the section meets detailed coverage and technical standards."
)
follow_up_queries: List[SearchQuery] = Field(
description="If grade is 'fail', specify further queries to gather missing insights."
)
</format>
"""


# Instructions for final sections (Introduction, Conclusion, etc.)

final_section_writer_instructions = """You are writing an essential concluding or introductory section for a deeply researched report, where each section (including intro and conclusion) must also reach 5–6 pages (1,500+ words) for thorough coverage.

<Section topic>
{section_topic}
</Section topic>

<Available report content>
{context}
</Available report content>

<Task>

1. Section-Specific Guidance:

For an Introduction:
- Use # for the report title (Markdown).
- Provide 5–6 pages (1,500+ words) introducing the topic’s relevance, context, and scope.
- Avoid tables, lists, or other structural elements here, maintaining a cohesive narrative flow.
- No sources section is needed.

For a Conclusion:
- Use ## for the section title (Markdown).
- Provide 5–6 pages (1,500+ words) synthesizing the insights from the entire report.
- If the topic has a comparative element, include exactly ONE table comparing the major points or findings.
- If non-comparative, you may include exactly ONE structural element (table OR short list) to distill the major takeaways.
- End with clear next steps or recommendations.
- No sources section is required in the conclusion.

2. Writing Approach:
- Maintain strong coherence with the body sections; reference and integrate their key findings or debates.
- Offer depth and narrative continuity, avoiding redundancy.
- Write formally and analytically, ensuring clarity and substance.

</Task>

<Quality Checks>
- Each introduction or conclusion must meet the 5–6 page (1,500+ word) requirement.
- Introduction:
  - # for title
  - No structural elements
  - No sources
- Conclusion:
  - ## for title
  - Only ONE structural element (table or list)
  - No sources
- Keep Markdown formatting consistent, no word count statements or extra commentary.
</Quality Checks>"""
