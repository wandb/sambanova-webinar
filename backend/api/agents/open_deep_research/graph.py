########## graph.py (NEW CODE) ##########
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_sambanova import ChatSambaNovaCloud

from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph
from langgraph.types import interrupt, Command

from .state import (
    ReportStateInput,
    ReportStateOutput,
    Sections,
    ReportState,
    SectionState,
    SectionOutputState,
    Queries,
    Feedback,
)
from .prompts import (
    report_planner_query_writer_instructions,
    report_planner_instructions,
    query_writer_instructions,
    section_writer_instructions,
    final_section_writer_instructions,
    section_grader_instructions,
)
from .configuration import Configuration
from .utils import tavily_search_async, deduplicate_and_format_sources, format_sections, perplexity_search
import os
import sys
import re

from api.data_types import DeepResearchReport, DeepResearchSection

os.environ["SAMBANOVA_API_KEY"] = "your_key_here"

writer_model = ChatSambaNovaCloud(
    model=Configuration.writer_model, temperature=0, max_tokens=8192
)

###############################################################################
# 1) A new helper function to parse out raw URLs, remove them from text, and
#    store them in citations. We do line-by-line or an entire text approach.
###############################################################################
def extract_urls_and_clean(content: str):
    """
    Scans the entire content for raw http/https URLs using a regex. For each URL:
      - we remove it from the text
      - we store a citation entry with "url" and "desc" = the line's text minus the URL.

    Returns: (cleaned_content, citations_list)
    Where citations_list is a list of dicts like: { "url": "...", "desc": "some text" }
    """
    # We'll keep a list of citations
    citations = []

    # We'll go line-by-line, scanning for URLs
    url_pattern = re.compile(r'(https?://[^\s]+)')

    lines = content.split("\n")
    cleaned_lines = []

    for line in lines:
        found_urls = url_pattern.findall(line)
        if not found_urls:
            # No URLs in this line, keep it as-is
            cleaned_lines.append(line)
        else:
            # We'll remove each URL from the line, store it in citations
            # We store the leftover text as "desc"
            new_line = line
            for url in found_urls:
                # store a citation
                # "desc" can be the line minus the URL
                # or a short snippet
                # We'll do a naive approach: everything except the url => desc
                desc = new_line.replace(url, "").strip()
                citations.append({"url": url, "desc": desc})
                # Remove the url from the line
                new_line = new_line.replace(url, "").strip()
            if new_line.strip():
                cleaned_lines.append(new_line.strip())

    cleaned_content = "\n".join(cleaned_lines).strip()
    return cleaned_content, citations

###############################################################################
# The rest of the nodes
###############################################################################

async def generate_report_plan(state: ReportState, config: RunnableConfig):
    """Generate the report plan."""
    topic = state["topic"]
    feedback = state.get("feedback_on_report_plan", None)

    configurable = Configuration.from_runnable_config(config)
    report_structure = configurable.report_structure
    number_of_queries = configurable.number_of_queries

    if isinstance(report_structure, dict):
        report_structure = str(report_structure)

    structured_llm = writer_model.with_structured_output(Queries)
    system_instructions_query = report_planner_query_writer_instructions.format(
        topic=topic,
        report_organization=report_structure,
        number_of_queries=number_of_queries
    )
    results = structured_llm.invoke([
        SystemMessage(content=system_instructions_query),
        HumanMessage(content="Generate search queries that will help with planning the sections of the report.")
    ])

    query_list = [q.search_query for q in results.queries]

    if isinstance(configurable.search_api, str):
        search_api = configurable.search_api
    else:
        search_api = configurable.search_api.value

    if search_api == "tavily":
        search_results = await tavily_search_async(query_list)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=1500, include_raw_content=False)
    elif search_api == "perplexity":
        search_results = perplexity_search(query_list)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=1000, include_raw_content=False)
    else:
        raise ValueError(f"Unsupported search API: {configurable.search_api}")

    system_instructions_sections = report_planner_instructions.format(
        topic=topic,
        report_organization=report_structure,
        context=source_str,
        feedback=feedback
    )

    if isinstance(configurable.planner_provider, str):
        planner_provider = configurable.planner_provider
    else:
        planner_provider = configurable.planner_provider.value

    if planner_provider == "openai":
        planner_llm = ChatOpenAI(model=configurable.planner_model)
    elif planner_provider == "groq":
        planner_llm = ChatGroq(model=configurable.planner_model)
    elif planner_provider == "sambanova":
        planner_llm = ChatSambaNovaCloud(model=configurable.planner_model, temperature=0, max_tokens=8192)
    else:
        raise ValueError(f"Unsupported search API: {configurable.search_api}")

    structured_llm = planner_llm.with_structured_output(Sections)
    report_sections = structured_llm.invoke([
        SystemMessage(content=system_instructions_sections),
        HumanMessage(content="Generate the sections of the report. Your response must include a 'sections' field containing a list of sections. Each section must have: name, description, plan, research, and content fields.")
    ])

    sections = report_sections.sections
    return {"sections": sections}

def human_feedback(state: ReportState, config: RunnableConfig) -> Command[Literal["generate_report_plan","build_section_with_web_research"]]:
    """ Get feedback on the report plan """
    sections = state["sections"]
    sections_str = "\n\n".join(
        f"Section: {section.name}\nDescription: {section.description}\nResearch needed: {'Yes' if section.research else 'No'}\n"
        for section in sections
    )

    feedback = interrupt(
        f"Please provide feedback on the following report plan. \n\n{sections_str}\n\n"
        "Does the report plan meet your needs? Pass 'true' to approve the report plan or provide feedback to regenerate the report plan:"
    )

    if isinstance(feedback, bool):
        return Command(goto=[
            Send("build_section_with_web_research", {"section": s, "search_iterations": 0})
            for s in sections
            if s.research
        ])
    elif isinstance(feedback, str):
        return Command(goto="generate_report_plan", update={"feedback_on_report_plan": feedback})
    else:
        raise TypeError(f"Interrupt value of type {type(feedback)} is not supported.")

def generate_queries(state: SectionState, config: RunnableConfig):
    section = state["section"]
    configurable = Configuration.from_runnable_config(config)
    number_of_queries = configurable.number_of_queries

    structured_llm = writer_model.with_structured_output(Queries)
    system_instructions = query_writer_instructions.format(
        section_topic=section.description,
        number_of_queries=number_of_queries
    )
    queries = structured_llm.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate search queries on the provided topic.")
    ])
    return {"search_queries": queries.queries}

async def search_web(state: SectionState, config: RunnableConfig):
    search_queries = state["search_queries"]
    configurable = Configuration.from_runnable_config(config)

    query_list = [q.search_query for q in search_queries]

    if isinstance(configurable.search_api, str):
        search_api = configurable.search_api
    else:
        search_api = configurable.search_api.value

    if search_api == "tavily":
        search_results = await tavily_search_async(query_list)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=5000, include_raw_content=True)
    elif search_api == "perplexity":
        search_results = perplexity_search(query_list)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=5000, include_raw_content=False)
    else:
        raise ValueError(f"Unsupported search API: {configurable.search_api}")

    return {"source_str": source_str, "search_iterations": state["search_iterations"] + 1}

def write_section(state: SectionState, config: RunnableConfig) -> Command[Literal[END,"search_web"]]:
    section = state["section"]
    source_str = state["source_str"]
    configurable = Configuration.from_runnable_config(config)

    system_instructions = section_writer_instructions.format(
        section_title=section.name,
        section_topic=section.description,
        context=source_str,
        section_content=section.content
    )

    section_content = writer_model.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate a report section based on the provided sources.")
    ])
    section.content = section_content.content

    # Grade
    section_grader_instructions_formatted = section_grader_instructions.format(
        section_topic=section.description,
        section=section.content
    )
    structured_llm = writer_model.with_structured_output(Feedback)
    feedback = structured_llm.invoke([
        SystemMessage(content=section_grader_instructions_formatted),
        HumanMessage(content="Grade the report and consider follow-up questions for missing information:")
    ])

    if feedback.grade == "pass" or state["search_iterations"] >= configurable.max_search_depth:
        return Command(update={"completed_sections": [section]}, goto=END)
    else:
        return Command(
            update={"search_queries": feedback.follow_up_queries, "section": section},
            goto="search_web"
        )

def write_final_sections(state: SectionState):
    section = state["section"]
    completed_report_sections = state["report_sections_from_research"]

    system_instructions = final_section_writer_instructions.format(
        section_title=section.name,
        section_topic=section.description,
        context=completed_report_sections
    )

    section_content = writer_model.invoke([
        SystemMessage(content=system_instructions),
        HumanMessage(content="Generate a report section based on the provided sources.")
    ])
    section.content = section_content.content
    return {"completed_sections": [section]}

def gather_completed_sections(state: ReportState):
    completed_sections = state["completed_sections"]
    completed_report_sections = format_sections(completed_sections)
    return {"report_sections_from_research": completed_report_sections}

def initiate_final_section_writing(state: ReportState):
    return [
        Send("write_final_sections", {
            "section": s,
            "report_sections_from_research": state["report_sections_from_research"]
        })
        for s in state["sections"]
        if not s.research
    ]

def compile_final_report(state: ReportState):
    """
    Compile the final report into a structured DeepResearchReport with parsed citations.
    - For each section in 'sections' (with updated content from 'completed_sections'),
      we remove raw URLs, store them in citations, then build a DeepResearchSection.
    - The final_report is just a concatenation of all cleaned sections.
    """
    sections = state["sections"]
    completed_map = {s.name: s.content for s in state["completed_sections"]}

    deep_sections = []
    for sec in sections:
        # fetch final content if completed
        final_content = completed_map.get(sec.name, sec.content or "")
        # parse out raw URLs => citations
        cleaned_content, citations = extract_urls_and_clean(final_content)

        ds = DeepResearchSection(
            name=sec.name,
            description=sec.description,
            content=cleaned_content.strip(),
            citations=citations
        )
        deep_sections.append(ds)

    # Build a final compiled text
    # For each section, we might show "## {section.name}\n{section.content}\n"
    # Then a small "Citations:\n..." block or combine at the end. 
    # The user specifically wants a single final block that includes these citations
    # "in a separate section"? We'll do it at the very end for global references.
    # Or we keep them local? The prompt says "the final report simply lists these citations at the end
    # in a separate section." We'll do that. We'll gather them globally:
    global_citations = []
    final_text_lines = []
    for ds in deep_sections:
        # Append a section header
        final_text_lines.append(f"# {ds.name}\n{ds.content}\n")
        # accumulate citations
        global_citations.extend(ds.citations)

    # Add a "References" or "Citations" block at the end
    if global_citations:
        final_text_lines.append("\n## Citations\n")
        for i, c in enumerate(global_citations, 1):
            # We'll show as: - (i) [desc] (url)
            desc = c["desc"] or f"Citation {i}"
            url = c["url"]
            final_text_lines.append(f"- [{desc}]({url})")

    final_report = "\n".join(final_text_lines).strip()

    with open("final_report.md", "w") as f:
        f.write(final_report)

    deep_research_report = DeepResearchReport(
        sections=deep_sections,
        final_report=final_report
    )

    # The graph expects "final_report" to be in the dict,
    # plus we'll store our structured object.
    return {
        "final_report": final_report,
        "deep_research_report": deep_research_report
    }

# Build sub-graph
section_builder = StateGraph(SectionState, output=SectionOutputState)
section_builder.add_node("generate_queries", generate_queries)
section_builder.add_node("search_web", search_web)
section_builder.add_node("write_section", write_section)

section_builder.add_edge(START, "generate_queries")
section_builder.add_edge("generate_queries", "search_web")
section_builder.add_edge("search_web", "write_section")

builder = StateGraph(ReportState, input=ReportStateInput, output=ReportStateOutput, config_schema=Configuration)
builder.add_node("generate_report_plan", generate_report_plan)
builder.add_node("human_feedback", human_feedback)
builder.add_node("build_section_with_web_research", section_builder.compile())
builder.add_node("gather_completed_sections", gather_completed_sections)
builder.add_node("write_final_sections", write_final_sections)
builder.add_node("compile_final_report", compile_final_report)

builder.add_edge(START, "generate_report_plan")
builder.add_edge("generate_report_plan", "human_feedback")
builder.add_edge("build_section_with_web_research", "gather_completed_sections")
builder.add_conditional_edges("gather_completed_sections", initiate_final_section_writing, ["write_final_sections"])
builder.add_edge("write_final_sections", "compile_final_report")
builder.add_edge("compile_final_report", END)

graph = builder.compile(checkpointer=MemorySaver())
