"""Agent implementations.

The nightly run is orchestrated as a Supervisor (Manning ch 12.3) that
coordinates four sub-agents:

- ingestion: pulls candidate papers from arXiv and other sources
- triage:    decides skip / skim / deep-read for each paper
- deep_read: produces structured analyses with provenance
- synthesis: writes the daily digest, emails it, commits to repo

Each sub-agent uses the ReAct + ToolNode pattern from Manning ch 11.2.
"""
