########## NEW CODE ##########
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

current_dir = os.getcwd()
repo_dir = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.append(repo_dir)


# NEW: We'll import the new classes
from api.data_types import DeepResearchReport, DeepResearchSection

os.environ["SAMBANOVA_API_KEY"] = "pass_in_from_env"

writer_model = ChatSambaNovaCloud(
    model=Configuration.writer_model, temperature=0, max_tokens=8192
)

# -------------------------------
# Helper function to parse citations
# -------------------------------
def extract_citations_and_clean(content: str):
    """
    Look for a line with either:
      - '### Sources' or
      - 'Sources:' or 'Sources:\n'
    Then parse each subsequent line of the form:
         Title : URL
    Return a list of {title, url}, plus the content with that block removed if desired.
    """
    lines = content.split("\n")
    citations = []
    new_lines = []
    in_sources_block = False

    for line in lines:
        lower_line = line.strip().lower()
        if "### sources" in lower_line or lower_line.startswith("sources:"):
            in_sources_block = True
            # skip adding this line to new_lines
            continue

        if in_sources_block:
            # we expect lines like "Title : URL"
            line_stripped = line.strip(" -*")  # remove bullets
            if not line_stripped:
                # blank line => end sources block
                in_sources_block = False
                continue
            # Attempt parse
            parts = line_stripped.split(" : ")
            if len(parts) == 2:
                the_title, the_url = parts
                citations.append({"title": the_title.strip(), "url": the_url.strip()})
            else:
                # Might be a partial or weird line => skip or end block if you prefer
                # We'll try a second pattern "title: URL"
                parts2 = line_stripped.split(": ")
                if len(parts2) == 2:
                    citations.append({"title": parts2[0].strip(), "url": parts2[1].strip()})
                else:
                    # no match => ignore
                    pass
        else:
            new_lines.append(line)

    # join new_lines => the content minus the sources
    cleaned_content = "\n".join(new_lines).strip()
    return cleaned_content, citations

# -------------------------------
# The main nodes
# -------------------------------

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

    feedback = interrupt(f"Please provide feedback on the following report plan. \n\n{sections_str}\n\n Does the report plan meet your needs? Pass 'true' to approve the report plan or provide feedback to regenerate the report plan:")

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
    """
    sections = state["sections"]
    # We map each "completed_section" back into the final sections
    completed_map = {s.name: s.content for s in state["completed_sections"]}

    # Build a list of DeepResearchSection
    deep_sections = []
    for sec in sections:
        # update the final content from the completed_map
        if sec.name in completed_map:
            sec.content = completed_map[sec.name]
        # parse citations
        cleaned_content, citations = extract_citations_and_clean(sec.content)
        deep_sec = DeepResearchSection(
            name=sec.name,
            description=sec.description,
            content=cleaned_content.strip(),
            citations=citations
        )
        deep_sections.append(deep_sec)

    # We'll join everything into final_report
    final_text = "\n\n".join([s.content for s in deep_sections])

    # Save to file if you wish
    with open("final_report.md", "w") as f:
        f.write(final_text)

    # Return a dict with "final_report" since the graph expects it
    # But also, we store a structured "DeepResearchReport"
    deep_research_report = DeepResearchReport(
        sections=deep_sections,
        final_report=final_text
    )
    return {"final_report": final_text, "deep_research_report": deep_research_report}

# Sub-graph
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
