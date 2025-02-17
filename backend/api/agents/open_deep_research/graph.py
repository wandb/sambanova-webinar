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

os.environ["SAMBANOVA_API_KEY"] = "YOUR_API_KEY"

# This is the writer model used throughout
writer_model = ChatSambaNovaCloud(
    model=Configuration.writer_model, temperature=0, max_tokens=8192
)

###############################################################################
# Helper function to parse references from "### Sources" or "## Sources" or "Sources:"
# block lines and store them as {section:..., url:..., desc:...}.
###############################################################################
def parse_reference_line(section_name: str, line: str) -> DeepCitation:
    """
    Given a reference line like "* Title: https://some_url"
    or "- Something: https://..."
    Parse into a DeepCitation object with title and url.
    """
    # remove leading bullet chars
    line = line.lstrip("*-0123456789. ").strip()
    
    # find the last occurrence of 'http'
    match = re.search(r'(https?://[^\s]+)', line)
    if not match:
        # no url found, treat entire line as title
        return DeepCitation(title=line, url="")
        
    url = match.group(1)
    # everything before the URL becomes the title
    title = line[:line.find(url)].strip().rstrip(':').strip()
    
    # If title ends with ": (Section: )", remove that part
    title = re.sub(r'\s*\(Section:\s*\)\s*$', '', title)
    
    return DeepCitation(title=title, url=url)

def extract_sources_block(section_name: str, text: str) -> (str, List[DeepCitation]):
    """
    Extract citations from the sources block and clean up the text.
    Only extracts citations from a dedicated sources section.
    """
    lines = text.split("\n")
    cleaned_lines = []
    references: List[DeepCitation] = []
    
    in_block = False
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Only detect start of references if it's a dedicated sources section
        if not in_block and (
            line.lower() == "### sources" or 
            line.lower() == "## sources" or
            line.lower() == "sources:"
        ):
            in_block = True
            i += 1
            continue
            
        if in_block:
            if not line or line.startswith('#'):  # empty line or new section ends block
                in_block = False
                i += 1
                continue
                
            ref = parse_reference_line(section_name, line)
            if ref.url:  # only add if we found a URL
                references.append(ref)
        else:
            # Keep non-reference lines
            cleaned_lines.append(lines[i])
        i += 1
    
    return '\n'.join(cleaned_lines).strip(), references

def remove_inline_urls(content: str) -> (str, List[DeepCitation]):
    """
    Remove inline URLs, but only if they follow specific citation patterns.
    """
    citations: List[DeepCitation] = []
    lines = content.split("\n")
    new_lines = []
    
    for line in lines:
        # Only match lines that are clearly citations with specific patterns
        citation_pattern = r'^([^:]+):\s*(https?://[^\s]+)$'
        match = re.match(citation_pattern, line.strip())
        
        if match:
            title = match.group(1).strip()
            url = match.group(2).strip()
            citations.append(DeepCitation(title=title, url=url))
        else:
            new_lines.append(line)
            
    return '\n'.join(new_lines).strip(), citations

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
       storing them in final citations.
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
        lines.append("\n## Citations\n")
        for c in all_citations:
            # Just use title and URL, no section reference
            if c.url:  # Only add if there's a URL
                lines.append(f"- [{c.title}]({c.url})")

    final_report_text = "\n".join(lines).strip()

    # Build a final DeepResearchReport
    dr_report = DeepResearchReport(
        sections=deep_sections,
        final_report=final_report_text,
        citations=all_citations
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
