# ADR-0002: Host the nightly run on GitHub Actions (v0.1)

**Status:** Accepted
**Date:** 2026-05-06
**Deciders:** Joseph Catanzarite (with Claude as collaborator)

## Context

We need a place for the nightly batch job to run. Constraints:
- Self-funded budget: $25/month ceiling for v0.1–v0.3
- Run is single overnight batch, not always-on
- Must support cron-like scheduling, secrets management, and artifact
  storage
- Should not require managing a server

## Decision

We host the nightly run on **GitHub Actions** using a scheduled workflow.

## Rationale

1. **Free tier is generous**: 2,000 minutes/month for private repos, far
   more than we need (a 30-min nightly job × 30 days = 900 min)
2. **Secrets management built in**: API keys go in GitHub Secrets, env vars
   are scoped to workflow runs
3. **Native scheduling**: cron syntax in workflow YAML
4. **Artifact storage**: digest files persist as workflow artifacts
5. **No infrastructure**: no VM to maintain, no Docker registry to manage,
   no SSH keys to rotate
6. **Version-control as a side effect**: the entire system lives in the repo,
   including the workflow that runs it

## Consequences

**Easier:**
- Setup is essentially `git push` and add secrets
- Cost is zero for our usage volume
- Migration to a self-hosted runner is supported if we outgrow it

**Harder:**
- State persistence across runs: GitHub Actions runners are ephemeral, so
  we use the `cache` action as a stopgap (state lives in `data/` directory).
  This is fragile — caches can be evicted. v0.4 must move state to an
  external store (S3, Postgres, or a dedicated VM).
- 6-hour max runtime per job (won't bite us for daily batches)
- Slight latency on free runners (cold start ~30s)

## Alternatives Considered

- **Cheap VM (DigitalOcean / Hetzner ~$5/mo)**: always-on, but we don't
  need always-on, and infra management is a tax.
- **AWS Lambda + EventBridge**: tighter than GH Actions for cron, but
  15-min hard timeout would force splitting the run into multiple invocations.
- **Self-hosted on user's machine + cron**: free, but requires the machine
  to be on at 3am, and setup/portability is harder than git push.

## References

- GitHub Actions billing: https://docs.github.com/en/billing
- GitHub Actions cache action: https://github.com/actions/cache
