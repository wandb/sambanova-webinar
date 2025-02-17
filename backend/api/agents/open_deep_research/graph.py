########## graph.py (UPDATED CODE) ##########
from typing import Literal, List
import os
import sys
import re

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

# We import our data models
from api.data_types import (
    DeepResearchReport,
    DeepResearchSection,
    # We add a new specialized class for references
    DeepCitation
)

os.environ["SAMBANOVA_API_KEY"] = "YOUR_API_KEY_HERE"

# This is the writer model used throughout
writer_model = ChatSambaNovaCloud(
    model=Configuration.writer_model, temperature=0, max_tokens=8192
)

###############################################################################
# Helper function to parse references from "### Sources" or "## Sources" or "Sources:"
# block lines and store them as {section:..., url:..., desc:...}.
###############################################################################
def extract_sources_block(section_name: str, text: str) -> (str, List[DeepCitation]):
    """
    1) Search for lines that match "### Sources", "## Sources", or "Sources:" (ignoring case).
    2) Take subsequent lines until a blank line or end of text as references.
       Typically they might look like: 
         * Groq: The AI Chip Startup Revolutionizing the Industry: https://www.33rdsquare.com/groq-the-newbie...
       or 
         - Another Title : https://some/link
    3) For each reference line, parse out "desc" vs "url".
       We'll do a naive parse:
         - If line has a final colon with something after it that looks like a URL, we store that in "url".
         - Everything prior is "desc".
    4) Return cleaned text (with those lines removed) and a list of DeepCitation objects with "section_name", "desc", "url".
    """
    lines = text.split("\n")
    cleaned_lines = []
    references: List[DeepCitation] = []

    in_block = False

    i = 0
    while i < len(lines):
        line = lines[i]
        line_stripped = line.strip().lower()
        # detect the start of references block
        if not in_block and (
            line_stripped.startswith("### sources") or 
            line_stripped.startswith("## sources") or
            line_stripped.startswith("sources:")
        ):
            # from next line onward, references
            in_block = True
            i += 1
            continue

        if in_block:
            # If we see a blank line => end references
            if not line.strip():
                in_block = False
                i += 1
                continue
            # This line is presumably a reference line, e.g. "* Title: https://..."
            # We attempt to parse it
            ref = parse_reference_line(section_name, line.strip())
            if ref:
                references.append(ref)
            # skip adding it to cleaned lines
        else:
            # normal line => keep
            cleaned_lines.append(line)
        i += 1

    cleaned_text = "\n".join(cleaned_lines).strip()
    return cleaned_text, references

def parse_reference_line(section_name: str, line: str) -> DeepCitation:
    """
    Given a reference line like "* Groq: Some Title: https://some_url"
    or "- Something: https://..."
    we find the final colon that has "http" after it, store that as url.
    The desc is everything prior to that.
    We store the 'section' as section_name.
    If we can't parse => None
    """
    # remove leading bullet chars
    # e.g. "* " or "- " or "1. "
    line = line.lstrip("*-0123456789. ").strip()
    # find the last occurrence of 'http'
    # or we find a pattern r'(https?://\S+)' => get that as the url
    match = re.search(r'(https?://[^\s]+)', line)
    if not match:
        # no url => store the entire line as desc
        return DeepCitation(section_name=section_name, desc=line, url="")
    url = match.group(1)
    # everything prior is desc
    idx = line.find(url)
    desc = line[:idx].strip().rstrip(":").strip()
    return DeepCitation(section_name=section_name, desc=desc, url=url)


###############################################################################
# Optional helper to remove raw embedded URLs from text
# if you still want to remove them outside the sources block
###############################################################################
def remove_inline_urls(content: str) -> (str, List[DeepCitation]):
    """
    If you want to remove additional raw URLs that appear in the text, you can parse them here.
    We'll store them as citations with desc being the line minus the url.
    But the user specifically asked for the references from sources block, so 
    this is purely optional if you still want to strip random inline URLs.
    """
    citations: List[DeepCitation] = []
    lines = content.split("\n")
    new_lines = []
    url_pattern = re.compile(r'(https?://[^\s]+)')

    for line in lines:
        matches = url_pattern.findall(line)
        if not matches:
            new_lines.append(line)
        else:
            replaced_line = line
            for u in matches:
                replaced_line = replaced_line.replace(u, "").strip()
                c = DeepCitation(section_name="", desc=replaced_line, url=u)
                citations.append(c)
            new_lines.append(replaced_line)
    final_text = "\n".join(new_lines).strip()
    return final_text, citations


###############################################################################
# The normal flow
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

    # do web search if needed
    if isinstance(configurable.search_api, str):
        search_api = configurable.search_api
    else:
        search_api = configurable.search_api.value

    if search_api == "tavily":
        search_results = await tavily_search_async(query_list)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=1000, include_raw_content=False)
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
        planner_llm = ChatOpenAI(model="gpt-3.5-turbo")  # example
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
    """ Write a section of the report with possible follow-up queries if failing. """
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
        # Publish the section
        return Command(update={"completed_sections": [section]}, goto=END)
    else:
        return Command(
            update={"search_queries": feedback.follow_up_queries, "section": section},
            goto="search_web"
        )


def write_final_sections(state: SectionState):
    """ Write final sections of the report with no research needed. """
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
    """ Gather completed research sections. """
    completed_sections = state["completed_sections"]
    completed_report_sections = format_sections(completed_sections)
    return {"report_sections_from_research": completed_report_sections}


def initiate_final_section_writing(state: ReportState):
    """
    Write any final sections using the Send API to parallelize the process
    (for sections that do not require research).
    """
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
    1) For each final completed section, remove the "### Sources" block if any,
       parse lines for references with parse_reference_line approach,
       storing them in final citations with "section=sec.name".
    2) Remove or keep other inline raw URLs if desired.
    3) Build the final text, store in DeepResearchReport with separate 'citations' list.
    """
    sections = state["sections"]
    completed_map = {s.name: s.content for s in state["completed_sections"]}

    deep_sections: List[DeepResearchSection] = []
    all_citations: List[DeepCitation] = []  # store the references from all sections

    for sec in sections:
        final_content = completed_map.get(sec.name, sec.content or "")

        # Step 1) Extract "### Sources" block
        cleaned_text, block_citations = extract_sources_block(sec.name, final_content)

        # Step 2) (OPTIONAL) also remove random inline URLs from cleaned_text
        # If you want to skip this, comment out next lines
        final_cleaned, inline_citations = remove_inline_urls(cleaned_text)

        # Merge citations
        all_citations.extend(block_citations)
        all_citations.extend(inline_citations)

        # build the DeepResearchSection
        ds = DeepResearchSection(
            name=sec.name,
            description=sec.description,
            content=final_cleaned.strip(),
            citations=[]  # we keep it empty, or store inline_citations if you prefer
        )
        deep_sections.append(ds)

    # Now build final text
    lines = []
    for ds in deep_sections:
        lines.append(f"# {ds.name}\n{ds.content}\n")

    # If we want to append citations block at the end:
    if all_citations:
        lines.append("## Citations\n")
        for c in all_citations:
            # we show something like: - [desc] (url) (Section: c.section_name)
            desc = c.desc or "No description"
            url = c.url
            lines.append(f"- [{desc}]({url}) (Section: {c.section_name})")

    final_report_text = "\n".join(lines).strip()

    # Save file
    with open("final_report.md", "w") as f:
        f.write(final_report_text)

    # Build a final DeepResearchReport with new 'citations' field
    # We'll store them in the top-level object for convenience
    dr_report = DeepResearchReport(
        sections=deep_sections,
        final_report=final_report_text,
        citations=all_citations  # new field
    )

    return {
        "final_report": final_report_text,
        "deep_research_report": dr_report
    }


# Build subgraph
section_builder = StateGraph(SectionState, output=SectionOutputState)
section_builder.add_node("generate_queries", generate_queries)
section_builder.add_node("search_web", search_web)
section_builder.add_node("write_section", write_section)

section_builder.add_edge(START, "generate_queries")
section_builder.add_edge("generate_queries", "search_web")
section_builder.add_edge("search_web", "write_section")

# Main graph
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
