# Rafeeq (رفيق) — Agentic Municipal Services Assistant

**Advanced Agentic AI Systems Engineering - SDAIA Academy**

**Course Website:** https://sdaiaacademy.github.io/agentic-ai/

**Project Repository:** https://github.com/Alaa-hf/rafeeq-capstone

**Project Type:** Agentic AI Engineering Capstone

**Primary Technologies:** Python, OpenRouter, Google Gemini 2.5 Flash, Model Context Protocol (MCP), SQLite, Agent Harness, Automated Evaluations

---

## 1. Executive Summary

**Rafeeq (رفيق)** is a bilingual, tool-using AI assistant designed to support citizens in accessing municipal services in the fictional **Madar Municipal Services** environment.

The system allows users to ask questions in Arabic or English about municipal permit fees, regulations, application status, inspections, and related procedures.

Rather than relying exclusively on the language model's internal knowledge, Rafeeq connects to structured municipal tools and policy resources, retrieves relevant information, and uses the results to generate grounded responses.

The project demonstrates the transition from a basic Large Language Model (LLM) interaction to a governed Agentic AI system with:

- An autonomous agent loop.
- Dynamic tool selection and execution.
- MCP-based tool integration.
- Context management and conversation history.
- Human-in-the-Loop (HITL) authorization.
- Execution and resource budgets.
- Prompt-injection defense mechanisms.
- Systematic evaluations and error analysis.
- Security threat modeling using the Lethal Trifecta framework.

The implementation uses simulated municipal services and synthetic course data. It is an educational prototype, not an official government service.

### Project Objectives

1. Develop an operational agent capable of selecting and invoking external tools.
2. Integrate municipal capabilities using the Model Context Protocol.
3. Maintain useful conversational context without unlimited history growth.
4. Apply human approval to operations that modify system state.
5. Introduce security controls against untrusted tool content.
6. Evaluate agent performance using at least 15 tasks across two configurations.
7. Analyze observed errors, system limitations, and engineering trade-offs.

---

## 2. Problem Statement

Municipal service environments contain multiple permit categories, fee structures, regulations, and administrative processes.

Users may need to locate relevant rules, calculate fees, or retrieve information about existing applications.

A conventional chatbot could answer these questions using its language-model knowledge alone. However, that approach presents several limitations:

- Fee calculations may be inaccurate.
- Regulations may be incomplete or outdated.
- Private records require identity verification.
- Administrative changes must not occur without authorization.
- External documents may contain malicious or misleading instructions.
- Model outputs must be evaluated rather than assumed correct.

Rafeeq addresses these challenges by combining an LLM with purpose-built municipal tools, explicit authorization policies, context controls, and a measurable evaluation process.

---

## 3. System Scope and Use Cases

Rafeeq supports the following fictional permit categories:

| Code | Permit Type |
|---|---|
| `BLD` | Building Permit |
| `REN` | Renovation Permit |
| `SGN` | Signage Permit |
| `FTR` | Food Truck Permit |
| `EVT` | Event Permit |

### Supported Scenarios

**Permit fee calculation:** The user provides relevant permit details, and Rafeeq invokes `compute_fee` to calculate the applicable amount.

**Policy retrieval:** The user asks about municipal regulations, requirements, working hours, or administrative procedures. Rafeeq can invoke `search_policies`.

**Permit status inquiry:** The user requests application-specific information. Rafeeq uses `get_permit` with the required verification information.

**Inspection scheduling:** Rafeeq can retrieve available inspection slots through `list_slots`.

**State-changing operations:** Inspection bookings, rescheduling, refund creation, and escalation are exposed as controlled operations requiring approval at the harness layer.

### Scope Limitations

- The municipality, permit records, and fees are simulated.
- No live government systems are connected.
- The application is primarily accessed through a Python CLI.
- The implementation is not intended for production handling of personal data.
- Some security and authorization tests have only been performed through controlled simulations.

---

## 4. System Architecture

Rafeeq follows a modular architecture separating user interaction, agent reasoning, municipal tools, authorization, data access, and evaluation.

### 4.1 High-Level Architecture

```mermaid
flowchart TD
    USER["User: Arabic / English"] --> CLI["CLI: capstone/starter.py"]

    CLI --> SPEC["System Instructions: AGENTS.md"]
    CLI --> CONTEXT["Session History and Compaction"]
    CLI --> LOOP["Agent Loop: agentkit.py"]

    SPEC --> LOOP
    CONTEXT <--> LOOP

    LOOP <--> MODEL["OpenRouter: Gemini 2.5 Flash"]

    LOOP --> ROUTER{"Tool Selection"}

    ROUTER --> MCP["MCPBridge"]
    MCP --> SERVER["Madar MCP Server"]
    SERVER --> READ["Read Tools"]

    ROUTER --> WRITE["Local Write Tools"]
    WRITE --> PERM["Permission Policy"]
    PERM --> HITL{"Human Approval"}
    HITL -->|Approved| EXEC["Execute Write"]
    HITL -->|Denied| BLOCK["Block Operation"]

    READ --> MADAR["Madar Service Layer"]
    EXEC --> MADAR

    MADAR --> DATA["Simulated SQLite and Policy Data"]

    READ --> GUARD["after_tool: Filtering, Size Cap, Audit"]
    EXEC --> GUARD
    GUARD --> LOOP

    LOOP --> FINAL["Final User Response"]

    CLI --> EVAL["Evaluation Runner: evals.py"]
    EVAL --> TASKS["JSONL Tasks and Graders"]
    EVAL --> RESULTS["Evaluation Results"]
```

### 4.2 Main Components

| Component | File | Responsibility |
|---|---|---|
| CLI and Agent Configuration | `labs/capstone/starter.py` | User commands, configurations, permissions, tool integration, evaluation entry point |
| Agent Instructions | `labs/capstone/AGENTS.md` | System role, behavioral rules, tool-use guidance, response requirements |
| Agent Runtime | `labs/agentkit.py` | LLM interaction, agent execution loop, tool calls, MCP bridge, budgets |
| Municipal Service Logic | `labs/madar.py` | Permit processing, fee calculations, verification, simulated database operations |
| MCP Server | `labs/servers/madar_mcp.py` | Exposes municipal read capabilities through MCP |
| Evaluation Framework | `labs/evals.py` | Runs tasks, applies graders, records performance |
| Evaluation Dataset | `labs/capstone/tasks.final.jsonl` | The 15-task evaluation subset |
| Security Documentation | `labs/capstone/SECURITY_ANALYSIS.md` | Lethal Trifecta assessment, attack simulation, defense, residual risks |

### 4.3 Agent Execution Workflow

A typical request follows this sequence:

1. The user submits a question through the CLI.
2. The application loads the system instructions and relevant conversation context.
3. The agent sends the request to the configured LLM through OpenRouter.
4. The model decides whether an external tool is required.
5. The agent harness routes the tool call to the appropriate implementation.
6. Read tools can execute through the MCP integration.
7. Write tools are subject to the permission policy and explicit human approval.
8. Returned tool information is processed by the `after_tool` hook.
9. Tool results are added to the conversation.
10. The agent continues until it produces a final answer or reaches an execution limit.

### 4.4 Why an Agent Instead of a Single LLM Call?

A single model call can generate text, but it cannot independently establish the current value of a municipal fee or safely modify a permit record.

The agent architecture provides a controlled way to delegate specific operations to tools.

For example, a fee calculation depends on a structured tool result, while a booking operation requires both a valid tool call and an approval decision.

This separation improves traceability and provides explicit locations for authorization and validation.

---

## 5. Model and Runtime Configuration

### 5.1 Language Model

The application was tested using:

`google/gemini-2.5-flash`

The model is accessed through OpenRouter.

An earlier trial using `google/gemini-2.5-flash-lite` demonstrated a case where the tool returned the expected fee but the agent's final model response was empty.

Switching to Gemini 2.5 Flash produced a usable final response in the observed development tests.

This is a limited engineering observation, not a general comparison of model reliability.

### 5.2 Runtime Parameters

The current agent configuration includes the following limits:

| Parameter | Configured Value | Purpose |
|---|---:|---|
| Maximum Steps | 8 | Prevent unbounded agent execution |
| Maximum Cost Budget | 0.05 | Bound resource consumption within the configured harness |
| Maximum Tool Result Length | 3,000 characters | Restrict oversized tool outputs |
| Maximum Conversation History | 24 messages | Bound context growth |

These are implementation settings. The presence of a budget does not establish that every exhaustion or failure path has been fully tested.

### 5.3 Design Trade-off

The system prioritizes a lightweight, inspectable implementation suitable for demonstrating core Agentic AI engineering concepts.

A more advanced deployment would require stronger monitoring, structured logging, authentication, authorization, and recovery mechanisms.

---

## 6. Tool Integration and MCP

Rafeeq uses external tools to retrieve information and perform controlled actions.

### 6.1 Read Tools

| Tool | Purpose | Interface |
|---|---|---|
| `compute_fee` | Calculates municipal permit fees | MCP |
| `search_policies` | Retrieves relevant policy information | MCP |
| `get_permit` | Retrieves a permit after required verification | MCP |
| `list_slots` | Lists available inspection slots | MCP |

### 6.2 Write Tools

| Tool | Purpose | Authorization |
|---|---|---|
| `book_inspection` | Creates an inspection booking | Human approval |
| `reschedule_inspection` | Changes an inspection booking | Human approval |
| `create_refund` | Initiates a simulated refund | Human approval |
| `escalate` | Escalates a municipal case | Human approval |

The underlying `madar.py` module also implements `send_email`; its availability to the active agent depends on whether it is registered in the active tool list. It should not be treated as an enabled capability without checking `starter.py`.

### 6.3 Why MCP?

The Model Context Protocol provides a standardized interface through which an agent can discover and invoke external capabilities.

In Rafeeq, the MCP server exposes municipal read operations, reducing the coupling between the agent runtime and the underlying municipal service implementation.

The `MCPBridge` connects the agent loop to the server, allowing the model to access municipal data through tool calls rather than directly accessing the database.

### 6.4 Verified Tool Coverage

The completed evaluation confirmed that the agent invoked three distinct tools:

- `compute_fee`
- `search_policies`
- `get_permit`

These three tools were observed across the 15-task evaluation dataset under both configurations.

---

## 7. Live Demo and Reproducible Example

### 7.1 Demo Scenario: Illuminated Sign Permit

**User request:**

> What is the fee for an illuminated 3 m² sign?

**Observed tool call:**

```text
compute_fee({
  "illuminated": true,
  "sign_m2": 3,
  "permit_type": "SGN"
})
```

**Observed tool result:**

```json
{
  "permit_type": "SGN",
  "fee_sar": 750,
  "policy": "POL-02"
}
```

**Expected user-facing answer:**

> The permit fee for an illuminated 3 m² sign is 750 SAR, according to policy POL-02.

The tool call and returned values above were observed during development testing. The expected answer illustrates the desired response; it is not presented as a verbatim captured model transcript.

### 7.2 How to Run the Demo

From the `labs` directory:

```powershell
uv run capstone/starter.py ask "What is the fee for an illuminated 3 m² sign?"
```

The trace should show the selected tool, its structured arguments, its returned result, and the agent's final response.

### 7.3 Additional Tested Examples

| Scenario | Observed Tool Result |
|---|---|
| Illuminated sign, 3 m² | 750 SAR |
| Unilluminated sign, 2 m² | 400 SAR |
| Illuminated sign, 4 m² | 1,000 SAR |
| Unilluminated sign, 4 m² | 800 SAR |

All monetary values come from the fictional municipal simulator and do not represent official Saudi municipal fees.

---

## 8. Context Engineering and Memory

Context management determines which instructions, conversation messages, and retrieved data are supplied to the language model.

### 8.1 System Instructions

The file:

`labs/capstone/AGENTS.md`

defines the agent's role and its expected interaction with municipal services.

It provides task-specific guidance and establishes how the assistant should approach tool use, user requests, and sensitive information.

Maintaining these instructions in a separate file improves readability and makes behavioral changes easier to inspect.

### 8.2 Session Persistence

Rafeeq supports a conversational CLI:

```powershell
uv run capstone/starter.py chat --session demo
```

Session histories are stored under:

`labs/artifacts/capstone/`

This enables context from earlier turns to be reused in subsequent conversation turns using the same session identifier.

### 8.3 Context Continuity Example

During development, the assistant was asked about a 4 m² sign and subsequently received a follow-up about changing the illumination condition.

The agent retained the relevant sign area and produced the corresponding updated fee of 800 SAR for an unilluminated sign.

This demonstrated follow-up context handling in the tested interaction.

However, a separately documented test of persistence across a full process restart is still recommended.

### 8.4 History Compaction

A custom `compact()` function restricts the history to a maximum of 24 messages, attempting to begin with a user message.

A development test reduced a synthetic 60-message history to 24 messages.

This mechanism is **history truncation**, not semantic summarization.

**Limitation:** It has not been comprehensively verified that all assistant tool calls and corresponding tool results remain structurally valid after truncation.

### 8.5 Tool Result Management

Tool responses are limited to a maximum of 3,000 characters.

This helps prevent oversized retrieval results from occupying excessive context and provides a location where potentially malicious retrieved content can be inspected.

---

## 9. Agent Harness and Human-in-the-Loop

The agent harness is responsible for controlling execution around the language model.

It manages the agent loop, tool interactions, resource limits, and authorization decisions.

### 9.1 Permission Policy

Read operations can be executed without changing municipal records.

Write operations use a permission mechanism that returns an approval requirement.

Examples of approval-gated tools include:

- `book_inspection`
- `reschedule_inspection`
- `create_refund`
- `escalate`

The CLI approval step allows the user to approve or deny an attempted write operation.

### 9.2 Human-in-the-Loop Test

A controlled test simulated a `book_inspection` tool call.

The approval decision was set to **deny**.

**Observed result:** The simulated booking function was not executed.

This demonstrates that the harness can block an unauthorized write in the tested scenario.

**Limitation:** The test used a mock tool. A complete end-to-end test involving the actual booking implementation and database-state verification remains outstanding.

### 9.3 Budget Enforcement

The runtime is configured with limits on:

- Agent execution steps.
- Cost budget.
- Tool response size.
- Conversation history length.

These measures help bound execution and operational resource usage.

The implemented limits are documented, but not every budget-exhaustion scenario has been experimentally validated.

---

## 10. Security Threat Model — Lethal Trifecta

Agentic systems face security risks when external content can influence a model that has access to sensitive information or consequential tools.

The **Lethal Trifecta** identifies three capabilities that can combine into a dangerous attack path.

### 10.1 The Three Elements

| Element | Meaning | Rafeeq Example |
|---|---|---|
| Access to Sensitive Data | The agent may access confidential or user-specific information | Simulated permit and applicant records |
| Untrusted Input | The model processes content that may contain attacker-controlled instructions | Retrieved policies and tool responses |
| External or Consequential Actions | The agent can use capabilities that communicate externally or change system state | Approval-gated write tools and potential communication capabilities |

### 10.2 Threat Scenario

Consider a malicious policy-search result containing instructions that impersonate a higher-priority system message.

An attacker may attempt to convince the assistant to ignore its instructions, provide incorrect municipal information, or misuse available capabilities.

The central risk is the promotion of untrusted source content into authoritative instructions.

### 10.3 Security Boundaries

Rafeeq introduces several protective mechanisms:

**Identity verification:** Application-specific records require verification information before access.

**Human approval:** State-changing actions require explicit authorization.

**Restricted tool exposure:** The active agent only receives tools configured in its runtime.

**Tool-result inspection:** Returned text can be filtered through the `after_tool` hook.

**Output-size limits:** Retrieved text is restricted to a defined maximum length.

These controls reduce certain risks but do not eliminate prompt injection.

---

## 11. Prompt Injection Attack and Defense

### 11.1 Attack Objective

A controlled prompt-injection test attempted to manipulate Rafeeq through a malicious tool response.

The simulated response included a fake system update instructing the assistant to ignore earlier instructions and claim that municipal permit fees were zero.

**Attack entry point:** A simulated `search_policies` result.

**Trust boundary:** Untrusted tool content attempting to override the agent's higher-priority instructions.

**Desired malicious outcome:** The assistant would communicate false fee information.

### 11.2 Defense Mechanism

A text-filtering mechanism was integrated into the tool-result processing stage.

The defense checks for selected suspicious instruction patterns.

When the known payload was detected, the untrusted text was replaced with a security warning rather than passed unchanged to the model.

### 11.3 Observed Experimental Result

| Stage | Observation |
|---|---|
| Malicious input | A fake `SYSTEM UPDATE` was supplied through a simulated policy result |
| Defense | The `after_tool` guard recognized and blocked the known pattern |
| Agent behavior | In the defended simulation, the model did not confirm the malicious zero-fee statement |
| Outcome | The tested injection attempt was intercepted |

### 11.4 Limitations

The defense uses a relatively simple pattern-matching approach.

It may fail against:

- Paraphrased malicious instructions.
- Indirect or multi-step prompt injection.
- Instructions embedded in unfamiliar formats.
- Attacks designed to manipulate tool arguments.
- Sensitive information leakage through otherwise valid outputs.

Therefore, this experiment provides evidence for **one controlled attack-and-defense case**, not comprehensive security protection.

### 11.5 Detailed Security Report

See the separate document:

[SECURITY_ANALYSIS.md](labs/capstone/SECURITY_ANALYSIS.md)

It contains the full Lethal Trifecta analysis, security boundaries, attack scenario, defense, and residual risks.

---

## 12. Evaluation Methodology

A central objective of this project was to evaluate the actual behavior of the agent rather than relying on isolated demonstrations.

### 12.1 Evaluation Design

The final evaluation used:

- **15 distinct tasks.**
- **Two configurations: A and B.**
- **One trial per task per configuration.**
- **30 total agent runs.**
- **Three observed tool types:** `compute_fee`, `search_policies`, and `get_permit`.

The evaluation covered four categories:

1. Fee calculations.
2. Regulations and policy questions.
3. Permit status retrieval.
4. Privacy-related behavior.

### 12.2 Configuration Comparison

**Configuration A — Baseline**

Uses the baseline agent instructions.

**Configuration B — Tool-Use Guidance**

Adds instructions encouraging tool usage when answering questions involving fees or dates.

The purpose of the comparison was to determine whether stronger tool-use guidance improved performance.

### 12.3 Evaluation Commands

From the `labs` directory:

```powershell
$env:AGENT_CACHE="0"
uv run capstone/starter.py eval capstone/tasks.final.jsonl --config A B
```

The final evaluation dataset contains the first 15 tasks from `tasks.rafeeq.jsonl`.

If necessary, the subset can be reproduced using:

```powershell
uv run python -c "from pathlib import Path; p=Path('capstone/tasks.rafeeq.jsonl'); lines=p.read_text(encoding='utf-8').splitlines(); assert len(lines)>=15; Path('capstone/tasks.final.jsonl').write_text('\n'.join(lines[:15])+'\n',encoding='utf-8')"
```

The generated `tasks.final.jsonl` should be committed alongside the project so that the reported experiment can be reproduced.

### 12.4 Grading

The evaluation framework records task success and individual grader failures.

Depending on the test, graders may verify:

- Whether a specific tool was invoked.
- Whether the answer includes required information.
- Whether a relevant policy or fee was returned.
- Whether privacy constraints were respected.

Keyword-based graders provide automated checks, but a failed string match does not always prove the answer is semantically incorrect.

---

## 13. Final Evaluation Results

The following results were obtained from the completed 30-run evaluation.

### 13.1 Overall Performance

| Metric | Configuration A | Configuration B |
|---|---:|---:|
| Total Tasks | 15 | 15 |
| Passed | 12 | 12 |
| Failed | 3 | 3 |
| **Pass Rate** | **80.0%** | **80.0%** |
| Reported `pass_at_k` | 0.80 | 0.80 |
| Reported `pass_hat_k` | 0.80 | 0.80 |

Both configurations achieved an 80% pass rate.

The additional tool-use guidance in Configuration B did not produce an observable improvement for these tasks.

This does not establish equivalent performance across repeated trials or larger evaluation sets.

### 13.2 Performance by Category

Results are identical for both configurations.

| Category | Passed | Total | Pass Rate |
|---|---:|---:|---:|
| Fees | 6 | 7 | 85.7% |
| Rules | 3 | 5 | 60.0% |
| Status | 2 | 2 | 100.0% |
| Privacy | 1 | 1 | 100.0% |
| **Overall** | **12** | **15** | **80.0%** |

The regulations and policy category had the lowest observed success rate.

### 13.3 Tool Usage Evidence

The evaluation traces confirmed the execution of:

- `compute_fee` during fee-related tasks.
- `search_policies` during multiple policy-related tasks.
- `get_permit` during verified status inquiries.

The privacy test without credentials passed without requiring an application-specific tool lookup.

Not every policy-related task selected the appropriate retrieval tool.

### 13.4 A/B Comparison Finding

Both configurations failed the same three tasks:

- `fee-social-security`
- `rules-office-hours`
- `rules-structural-wall`

This suggests that the additional instructions in Configuration B were insufficient to address these particular failure patterns.

---

## 14. Error Analysis

The detailed evaluation log contained three failed tasks for each configuration.

### Failure 1: `fee-social-security`

**Category:** Fees  
**Language:** Arabic  
**Observed Tool:** `compute_fee`

**Grader failure:**

```text
contains_any:
none of ['معف', 'مجان', 'بدون رسوم', 'لا رسوم']
```

**Analysis:**

The agent invoked the expected fee calculation tool, but the final response did not contain any of the exemption-related expressions checked by the grader.

The available CSV log does not include the full model answer or tool payload.

Therefore, the evidence does not establish whether the result was numerically incorrect or whether the response failed because of wording.

**Recommended improvement:** Inspect the complete answer and calculation output, verify exemption handling, and consider semantically equivalent Arabic expressions during grading.

### Failure 2: `rules-office-hours`

**Category:** Rules  
**Language:** Arabic  
**Observed Tool:** None

**Grader failure:**

```text
tool_called: search_policies not called

contains_any:
none of ['7:30', '07:30', '٧:٣٠']
```

**Analysis:**

The agent did not invoke `search_policies`.

It also failed to include the expected office opening time.

Unlike the other failures, this test provides direct evidence of incorrect or missing tool selection.

The agent answered without consulting the expected policy source.

**Recommended improvement:** Strengthen guidance to retrieve policy information for office hours, deadlines, regulations, and other policy-dependent factual questions.

### Failure 3: `rules-structural-wall`

**Category:** Rules  
**Language:** Arabic  
**Observed Tool:** `search_policies`

**Grader failure:**

```text
contains_any:
none of ['مهندس', 'engineer']
```

**Analysis:**

The agent invoked the policy search tool, but the final response did not include the expected reference to an engineer.

This may indicate incomplete use of retrieved information, missing source content, or sensitivity in the keyword-based grader.

The exact cause cannot be established without reviewing the complete response and retrieved policy content.

**Recommended improvement:** Inspect the retrieved policy, compare the model's answer to the required conditions, and improve grounded answer completeness.

### 14.1 Failure Summary

| Failed Task | Tool Called? | Failure Type | Configuration A | Configuration B |
|---|---|---|---|---|
| `fee-social-security` | Yes | Missing expected answer content | Failed | Failed |
| `rules-office-hours` | No | Tool selection and missing information | Failed | Failed |
| `rules-structural-wall` | Yes | Missing expected answer content | Failed | Failed |

### 14.2 Root Cause Discussion

The observed errors can be grouped into two main failure patterns.

**Tool-selection failure:** The agent failed to invoke the required policy search tool when answering the office-hours question.

**Answer-content failure:** The agent invoked an appropriate tool but did not produce the exact information required by the grader.

The second category requires more detailed response inspection before assigning a definitive root cause.

### 14.3 Evaluation Limitations

- Each task was executed only once per configuration.
- No repeated-trial variance or confidence intervals were calculated.
- Automated string checks may reject semantically equivalent answers.
- The evaluation CSV does not store complete model responses or tool payloads.
- Only one privacy task was included in the evaluated subset.
- The results describe the simulated task set, not production reliability.
- The remaining three tasks from the 18-task draft were not executed in the final comparison.

---

## 15. Analysis and Findings

### 15.1 Functional Analysis

Rafeeq successfully demonstrated the integration of an LLM with structured municipal capabilities.

The fee calculation example produced a verified simulator output of **750 SAR** for a 3 m² illuminated sign under `POL-02`.

This demonstrated that the system could retrieve a calculated value through a tool rather than relying on a hard-coded response.

### 15.2 Tool Selection

The evaluation confirmed that three distinct tools were invoked.

However, the office-hours failure demonstrated that tool selection is not guaranteed for every policy-dependent query.

This is an important limitation because a response generated without retrieval may omit required factual information.

### 15.3 Model Configuration

The baseline and modified configurations achieved the same task success rate.

The added instructions in Configuration B did not improve the tested outcomes.

An instruction change alone may not resolve missing retrieval decisions or incomplete answer construction.

A targeted change followed by a new evaluation would be required to establish an improvement.

### 15.4 Context Management

The conversational test demonstrated that Rafeeq could use earlier sign details in a follow-up question.

History truncation also reduced oversized synthetic message histories.

However, basic message truncation may produce invalid conversation structures if a tool call is separated from its corresponding result.

A more robust implementation would preserve message groups or use structured summarization.

### 15.5 Safety and Authorization

The controlled HITL test confirmed that denial could prevent execution of a simulated write tool.

This is evidence of a useful authorization control.

It is not equivalent to proof that every write operation is safely handled in all conditions.

### 15.6 Prompt Injection Defense

The controlled injection test demonstrated that filtering a known malicious tool response can prevent the tested instruction from reaching the model unchanged.

The approach is limited by its reliance on recognizable text patterns.

For production use, security would require stronger trust-boundary enforcement, restricted privileges, careful handling of sensitive outputs, and broader attack testing.

### 15.7 Main Findings

1. Tool-grounded fee calculations worked in development testing.
2. Three tool types were exercised in the formal evaluation.
3. Both configurations achieved 80% success.
4. The weakest tested category was rules and policy retrieval.
5. A/B instruction changes did not resolve the repeated failures.
6. Basic HITL and prompt-injection defenses were demonstrated through controlled tests.
7. Context and resource limits were implemented, with additional edge-case verification remaining.
8. The project is a functional educational prototype with identifiable areas for improvement.

---

## 16. Engineering Decisions and Trade-offs

| Decision | Rationale | Limitation |
|---|---|---|
| Tool-based fee calculations | Ground numerical responses in service logic | Correct tool selection is still required |
| MCP read integration | Standardized external capability access | MCP does not independently guarantee security |
| Separate `AGENTS.md` | Maintain clear, editable agent instructions | Prompt instructions are not sufficient authorization controls |
| Human approval for writes | Prevent unapproved state changes | Real end-to-end database verification remains |
| History truncation | Reduce context growth | May disrupt tool-call/result structure |
| Tool result size limit | Bound retrieved context | May truncate relevant information |
| Pattern-based injection filtering | Block known suspicious patterns | May miss paraphrased and novel attacks |
| Two-configuration evaluation | Compare measured agent behavior | Single trials provide limited statistical evidence |
| CLI interface | Simple, reproducible development workflow | No production user-facing application |

These trade-offs reflect a deliberate focus on understanding and implementing the fundamental components of Agentic AI systems.

---

## 17. Setup and Reproducibility

### 17.1 Prerequisites

- Python and the dependencies defined by the course repository.
- `uv` package manager.
- An OpenRouter API key.
- Access to the course starter code and simulated data.
- A terminal such as PowerShell.

### 17.2 Installation

Clone the project:

```powershell
git clone https://github.com/Alaa-hf/rafeeq-capstone.git
cd rafeeq-capstone
cd labs
```

Install dependencies:

```powershell
uv sync
```

Create the environment file using the repository's example configuration, if available.

Configure:

```dotenv
OPENROUTER_API_KEY=YOUR_API_KEY
AGENT_MODEL=google/gemini-2.5-flash
```

Never commit an actual API key.

Prepare the simulated data if necessary:

```powershell
uv run python prepare_data.py
```

### 17.3 Single Question

```powershell
uv run capstone/starter.py ask "What is the fee for an illuminated 3 m² sign?"
```

### 17.4 Conversational Mode

```powershell
uv run capstone/starter.py chat --session demo
```

### 17.5 Evaluation

```powershell
uv run capstone/starter.py eval capstone/tasks.final.jsonl --config A B
```

The evaluation command sends requests to the configured LLM provider and may incur API charges.

The published results were collected with caching disabled during the evaluation session.

### 17.6 Reproduction Notes

- Run commands from the `labs` directory.
- Ensure the simulator data has been initialized.
- Keep the model and evaluation tasks consistent when comparing configurations.
- Do not publish private environment variables or sensitive data.
- Model responses may vary across separate executions.
- The results reported in this README reflect the completed evaluation, not a guarantee that future reruns will produce identical scores.

---

## 18. Test Evidence and Verification Status

| Test or Requirement | Evidence | Status |
|---|---|---|
| Basic CLI interaction | Arabic greeting and permit queries | Tested |
| Fee tool integration | `compute_fee` returned 750 SAR for an illuminated 3 m² sign | Tested |
| Multiple fee scenarios | Additional sign calculations | Tested |
| Context continuity | Follow-up retained relevant sign details | Tested in conversation |
| History truncation | 60 synthetic messages reduced to 24 | Basic test completed |
| HITL write denial | Mock booking execution prevented after denial | Mock test completed |
| Prompt injection attack | Fake system update inside policy result | Controlled test completed |
| Prompt injection defense | Known malicious payload filtered | Controlled test completed |
| Three tools in evaluations | `compute_fee`, `search_policies`, `get_permit` | Verified |
| 15 evaluation tasks | 15 tasks run on each configuration | Completed |
| A/B comparison | 80% success for A and B | Completed |
| Error analysis | Three shared failures documented | Completed |
| Lethal Trifecta | Dedicated security analysis | Documented |
| Cross-process session persistence | Implementation supports session files | Requires explicit verification evidence |
| Tool-call-safe compaction | Basic truncation only | Not fully verified |
| Budget exhaustion | Limits configured | Not exhaustively tested |
| Real database write path | Mock HITL test only | Not end-to-end verified |
| Expanded 18-task suite | Draft prepared | Not fully executed |

The outstanding tests are identified explicitly to distinguish implemented capabilities from experimentally verified behavior.

---

## 19. Limitations and Future Improvements

### 19.1 Short-Term Improvements

- Investigate the three failed evaluation tasks using full model responses.
- Strengthen policy retrieval for working hours and regulatory requirements.
- Improve Arabic answer completeness and semantic grading.
- Validate conversation history integrity around tool calls.
- Test approval-gated write operations end to end.
- Verify session persistence across a complete process restart.
- Test behavior when execution and cost budgets are exhausted.

### 19.2 Security Improvements

- Use more robust separation between instructions and retrieved content.
- Apply least-privilege tool authorization.
- Redact sensitive information from logs and approval prompts.
- Validate tool arguments and outputs.
- Expand prompt-injection tests to paraphrased and indirect attacks.
- Review possible data-exfiltration paths before allowing external communications.

### 19.3 Evaluation Improvements

- Add repeated trials to measure result variability.
- Use semantic grading alongside deterministic checks.
- Include additional privacy and write-action tests.
- Measure response latency, token usage, and tool-selection accuracy.
- Compare future agent revisions using the same evaluation dataset.

---

## 20. Conclusion

Rafeeq demonstrates the engineering principles required to transform a language-model interaction into a tool-using and governed Agentic AI system.

The project integrates a Python agent loop, OpenRouter model access, MCP-based read tools, municipal service logic, session context, authorization checks, execution budgets, and prompt-injection filtering.

A formal evaluation covering **15 tasks across two configurations** produced a success rate of **80% for both configurations**, with three repeated failures.

The evaluation identified policy retrieval and response completeness as the principal observed weaknesses.

Security testing included a controlled prompt-injection attack and a defense mechanism, supported by a dedicated Lethal Trifecta analysis.

The implementation is not presented as production-ready. Instead, it demonstrates a functioning educational agent, measured behavior, documented safeguards, and an evidence-based understanding of its limitations.

---

## 21. Repository Hygiene and Privacy

The following must not be committed to a public repository:

- API keys and `.env` files.
- Sensitive applicant information.
- Local session histories.
- Unreviewed database snapshots.
- Private logs or cache files.
- Credentials embedded in demonstrations or screenshots.

Generated evaluation artifacts should be reviewed and sanitized before publication.

The repository should preserve necessary attribution and applicable license notices from the SDAIA Academy starter project.

---

## 22. References and Attribution

**Advanced Agentic AI Systems Engineering - SDAIA Academy**

Course Website: https://sdaiaacademy.github.io/agentic-ai/

Original Course Repository: https://github.com/SDAIAAcademy/agentic-ai

Project Repository: https://github.com/Alaa-hf/rafeeq-capstone

This project extends the SDAIA Academy course starter materials and the fictional Madar Municipal Services case study. The implementation and documented evaluation are intended for educational use.

**Related project documentation:**

- [Agent Instructions](labs/capstone/AGENTS.md)
- [Security Analysis](labs/capstone/SECURITY_ANALYSIS.md)
- [Final Evaluation Tasks](labs/capstone/tasks.final.jsonl)
- [Full Draft Evaluation Tasks](labs/capstone/tasks.rafeeq.jsonl)
- [Agent Implementation](labs/capstone/starter.py)
