########## graph.py (UPDATED CODE) ##########
import functools
from typing import Literal, List
import os
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from langchain_sambanova import ChatSambaNovaCloud
from langchain_fireworks import ChatFireworks

from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph
from langgraph.types import interrupt, Command

from config.model_registry import model_registry

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
    DeepCitation
)



###############################################################################
# 1) Utility: parse a reference line from the sources block
###############################################################################
def parse_reference_line(line: str) -> DeepCitation:
    """
    If the line has an http/https link, store that as url, everything before is "title".
    If no URL found, return a citation with empty url => skip it upstream.
    """
    # remove bullet chars
    line = line.lstrip("*-0123456789. ").strip()
    # find a link
    match = re.search(r'(https?://[^\s]+)', line)
    if not match:
        # no link => skip
        return DeepCitation(title="", url="")  # no URL
    url = match.group(1)
    # everything prior to the url is the title
    idx = line.find(url)
    title = line[:idx].strip(" :")
    return DeepCitation(title=title, url=url)

def extract_sources_block(section_text: str) -> (str, List[DeepCitation]):
    """
    If there's a block after ### Sources or ## Sources or 'Sources:' 
    parse them line by line. 
    Remove that block from the text. Return cleaned text + references array.
    """
    lines = section_text.split("\n")
    cleaned_lines = []
    citations: List[DeepCitation] = []

    in_sources = False

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        lower_line = line.lower().strip()
        # detect the start
        if not in_sources and (lower_line == "### sources" or lower_line == "## sources" or lower_line == "sources:"):
            # from next line onward => references
            in_sources = True
            i += 1
            continue

        if in_sources:
            # if blank or new heading => end
            if not line.strip() or re.match(r'#+\s', line):
                # end
                in_sources = False
                # do not add line to cleaned
                i += 1
                continue
            # parse the line
            ref = parse_reference_line(line)
            # if no url => skip
            if ref.url:
                citations.append(ref)
        else:
            cleaned_lines.append(line)
        i += 1

    new_text = "\n".join(cleaned_lines).strip()
    return new_text, citations

###############################################################################
# 2) Optional remove inline references with a pattern
###############################################################################
def remove_inline_citation_lines(text: str) -> (str, List[DeepCitation]):
    """
    If you want to forcibly remove lines that look like a bullet with 'http' 
    but are not in the sources block, you can parse them here.
    We'll only remove lines that start with "* " or "- " or some bullet + a link.
    """
    lines = text.split("\n")
    new_lines = []
    found: List[DeepCitation] = []

    for line in lines:
        trimmed = line.strip()
        # check if it starts with bullet
        if re.match(r'^(\*|-)\s+', trimmed):
            # check for a url
            match = re.search(r'(https?://[^\s]+)', trimmed)
            if match:
                # parse
                ref = parse_reference_line(trimmed)
                if ref.url:  # store
                    found.append(ref)
                # skip line
                continue
        # else keep
        new_lines.append(line)
    return "\n".join(new_lines), found

###############################################################################
# The normal nodes
###############################################################################

async def generate_report_plan(writer_model, planner_model, state: ReportState, config: RunnableConfig):
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

    structured_llm = planner_model.with_structured_output(Sections)
    report_sections = structured_llm.invoke([
        SystemMessage(content=system_instructions_sections),
        HumanMessage(content="Generate the sections of the report. Your response must include a 'sections' field containing a list of sections. Each section must have: name, description, plan, research, and content fields.")
    ])

    sections = report_sections.sections
    return {"sections": sections}

def human_feedback(state: ReportState, config: RunnableConfig):
    sections = state["sections"]
    sec_str = "\n\n".join(
        f"Section: {s.name}\nDescription: {s.description}\nResearch: {s.research}\n"
        for s in sections
    )
    fb = interrupt(
        f"Please provide feedback on the following plan:\n\n{sec_str}\n\n"
        "type 'true' to accept, or text to revise."
    )
    if isinstance(fb, bool):
        return Command(goto=[
            Send("build_section_with_web_research", {"section": s, "search_iterations": 0})
            for s in sections
            if s.research
        ])
    elif isinstance(fb, str):
        return Command(goto="generate_report_plan", update={"feedback_on_report_plan": fb})
    else:
        raise ValueError("interrupt unknown")

def generate_queries(writer_model, state: SectionState, config: RunnableConfig):
    sec = state["section"]
    configurable = Configuration.from_runnable_config(config)
    structured_llm = writer_model.with_structured_output(Queries)
    sys_inst = query_writer_instructions.format(
        section_topic=sec.description,
        number_of_queries=configurable.number_of_queries
    )
    queries = structured_llm.invoke([
        SystemMessage(content=sys_inst),
        HumanMessage(content="Generate search queries.")
    ])
    return {"search_queries": queries.queries}

async def search_web(state: SectionState, config: RunnableConfig):
    sq = state["search_queries"]
    configurable = Configuration.from_runnable_config(config)
    query_list = [q.search_query for q in sq]

    if isinstance(configurable.search_api, str):
        search_api = configurable.search_api
    else:
        search_api = configurable.search_api.value

    if search_api == "tavily":
        sr = await tavily_search_async(query_list)
        src_str = deduplicate_and_format_sources(sr, max_tokens_per_source=5000, include_raw_content=True)
    elif search_api == "perplexity":
        sr = perplexity_search(query_list)
        src_str = deduplicate_and_format_sources(sr, max_tokens_per_source=5000, include_raw_content=False)
    else:
        src_str = "No search"

    return {
        "source_str": src_str,
        "search_iterations": state["search_iterations"] + 1
    }

def write_section(writer_model, state: SectionState, config: RunnableConfig) -> Command[Literal[END,"search_web"]]:
    sec = state["section"]
    src = state["source_str"]
    sys_inst = section_writer_instructions.format(
        section_title=sec.name,
        section_topic=sec.description,
        context=src,
        section_content=sec.content
    )
    content = writer_model.invoke([
        SystemMessage(content=sys_inst),
        HumanMessage(content="Write the section.")
    ])
    sec.content = content.content

    # now we grade
    grader_inst = section_grader_instructions.format(
        section_topic=sec.description,
        section=sec.content
    )
    structured_llm = writer_model.with_structured_output(Feedback)
    fb = structured_llm.invoke([
        SystemMessage(content=grader_inst),
        HumanMessage(content="Grade it")
    ])

    if fb.grade == "pass" or state["search_iterations"] >= Configuration.from_runnable_config(config).max_search_depth:
        return Command(update={"completed_sections": [sec]}, goto=END)
    else:
        return Command(
            update={"search_queries": fb.follow_up_queries, "section": sec},
            goto="search_web"
        )

def write_final_sections(writer_model, state: SectionState):
    sec = state["section"]
    rep = state["report_sections_from_research"]
    sys_inst = final_section_writer_instructions.format(
        section_title=sec.name,
        section_topic=sec.description,
        context=rep
    )
    content = writer_model.invoke([
        SystemMessage(content=sys_inst),
        HumanMessage(content="Write final section.")
    ])
    sec.content = content.content
    return {"completed_sections": [sec]}

def gather_completed_sections(state: ReportState):
    comps = state["completed_sections"]
    rep = format_sections(comps)
    return {"report_sections_from_research": rep}

def initiate_final_section_writing(state: ReportState):
    return [
        Send("write_final_sections", {"section": s, "report_sections_from_research": state["report_sections_from_research"]})
        for s in state["sections"]
        if not s.research
    ]

def compile_final_report(state: ReportState):
    sections = state["sections"]
    completed_map = {s.name: s.content for s in state["completed_sections"]}

    deep_sections: List[DeepResearchSection] = []
    all_citations: List[DeepCitation] = []

    for sec in sections:
        content = completed_map.get(sec.name, sec.content or "")

        # 1) strip any sources block
        cleaned, block_refs = extract_sources_block(content)
        # 2) optionally remove bullet lines that contain URLs but are not in sources block
        # if we want to keep inline links in the text, skip this step or tweak it
        final_cleaned, inline_refs = remove_inline_citation_lines(cleaned)

        # combine
        # only keep references that have a valid url
        block_refs = [r for r in block_refs if r.url.strip()]
        inline_refs = [r for r in inline_refs if r.url.strip()]
        all_citations.extend(block_refs)
        all_citations.extend(inline_refs)

        deep_sections.append(
            DeepResearchSection(
                name=sec.name,
                description=sec.description,
                content=final_cleaned.strip(),
                citations=[]  # we skip local citations array
            )
        )

    # build final text
    lines = []
    for ds in deep_sections:
        lines.append(f"# {ds.name}\n{ds.content}\n")

    # final citations at end
    if all_citations:
        lines.append("## Citations\n")
        for c in all_citations:
            title = c.title.strip() or "Untitled"
            url = c.url.strip()
            lines.append(f"- [{title}]({url})")

    final_text = "\n".join(lines).strip()

    report = DeepResearchReport(
        sections=deep_sections,
        final_report=final_text,
        citations=all_citations
    )
    return {"final_report": final_text, "deep_research_report": report}


def get_graph(api_key: str):

    if model_registry.get_current_provider() == "fireworks":    
        writer_model = ChatFireworks(model=Configuration.writer_model, temperature=0, max_tokens=8192, api_key=api_key)
        planner_model = ChatFireworks(model=Configuration.planner_model, temperature=0, max_tokens=8192, api_key=api_key)
        
    else:
        writer_model = ChatSambaNovaCloud(model=Configuration.writer_model, temperature=0, max_tokens=8192, api_key=api_key)
        planner_model = ChatSambaNovaCloud(model=Configuration.planner_model, temperature=0, max_tokens=8192, api_key=api_key)

    # Build subgraph
    section_builder = StateGraph(SectionState, output=SectionOutputState)
    section_builder.add_node("generate_queries", functools.partial(generate_queries, writer_model))
    section_builder.add_node("search_web", search_web)
    section_builder.add_node("write_section", functools.partial(write_section, writer_model))

    section_builder.add_edge(START, "generate_queries")
    section_builder.add_edge("generate_queries", "search_web")
    section_builder.add_edge("search_web", "write_section")

    builder = StateGraph(ReportState, input=ReportStateInput, output=ReportStateOutput, config_schema=Configuration)
    builder.add_node("generate_report_plan", functools.partial(generate_report_plan, writer_model, planner_model))
    builder.add_node("human_feedback", human_feedback)
    builder.add_node("build_section_with_web_research", section_builder.compile())
    builder.add_node("gather_completed_sections", gather_completed_sections)
    builder.add_node("write_final_sections", functools.partial(write_final_sections, writer_model))
    builder.add_node("compile_final_report", compile_final_report)

    builder.add_edge(START, "generate_report_plan")
    builder.add_edge("generate_report_plan", "human_feedback")
    builder.add_edge("build_section_with_web_research", "gather_completed_sections")
    builder.add_conditional_edges("gather_completed_sections", initiate_final_section_writing, ["write_final_sections"])
    builder.add_edge("write_final_sections", "compile_final_report")
    builder.add_edge("compile_final_report", END)

    return builder