# 12-Week Launch Plan

**Atom ID:** 12-week-launch-plan
**Status:** ACTIVE
**References:** 4 cross-references in knowledge base corpus (2 filesystem_triage entries)

---

## Overview

This plan covers the final push from 80% roadmap completion (187/235 tasks) to production-ready status. Organized into three 4-week sprints, each with clear deliverables and acceptance criteria.

## Current State

- **Completed:** 187/235 tasks (80%)
- **Remaining:** 48 tasks across Phases 5-6
- **Test coverage:** 62.7% (1,463 tests)
- **API:** 38 endpoints, documented and tested
- **Web UI:** Complete (React + D3.js)

## Sprint 1: Hardening (Weeks 1-4)

**Theme:** Close gaps in existing features, improve test coverage, fix known issues.

### Week 1-2: Test Coverage Push

| Task | Target | Current | Priority |
|------|--------|---------|----------|
| Unit test coverage | 80% | 62.7% | P0 |
| API integration tests | All 38 endpoints | Partial | P0 |
| Atomization edge cases | 10 new test cases | 0 | P1 |
| Search relevance tests | MRR@10 benchmarks | Informal | P1 |

### Week 3-4: Bug Fixes and Polish

| Task | Scope | Priority |
|------|-------|----------|
| Fix PDF parsing edge cases | document-atomizer.ts | P1 |
| Improve semantic chunker confidence thresholds | semantic-chunker.ts | P1 |
| Web UI responsive design fixes | web-react/ | P2 |
| API error message consistency | api.ts | P2 |
| Rate limiter configuration documentation | docs/ | P2 |

**Sprint 1 Exit Criteria:**
- [ ] Test coverage >= 80%
- [ ] All 38 API endpoints have integration tests
- [ ] No known P0 bugs

## Sprint 2: Production Infrastructure (Weeks 5-8)

**Theme:** Build deployment pipeline, monitoring, and backup automation.

### Week 5-6: Docker and CI/CD

| Task | Deliverable | Priority |
|------|-------------|----------|
| Optimize Dockerfile | Multi-stage build, non-root user | P0 |
| Docker Compose production config | docker-compose.prod.yml | P0 |
| GitHub Actions CI pipeline | Lint + test + build on PR | P0 |
| GitHub Actions CD pipeline | Deploy to Fly.io on main push | P1 |

### Week 7-8: Monitoring and Backup

| Task | Deliverable | Priority |
|------|-------------|----------|
| Health check endpoint hardening | /api/health with component status | P0 |
| Structured logging (JSON) | Winston or pino integration | P1 |
| Automated backup scheduling | Cron-based SQLite backup | P1 |
| Backup restore verification | Automated restore test | P1 |
| Performance monitoring | Response time tracking | P2 |

**Sprint 2 Exit Criteria:**
- [ ] Docker build succeeds and passes tests
- [ ] CI pipeline runs on every PR
- [ ] Backup/restore cycle verified
- [ ] Health endpoint reports component status

## Sprint 3: Launch Preparation (Weeks 9-12)

**Theme:** Documentation, public launch readiness, and final validation.

### Week 9-10: Documentation

| Task | Deliverable | Priority |
|------|-------------|----------|
| README overhaul | Installation + usage + screenshots | P0 |
| API documentation update | All 38 endpoints with examples | P0 |
| Architecture documentation | Updated diagrams | P1 |
| Contributing guide update | Development workflow | P1 |

### Week 11-12: Launch Validation

| Task | Deliverable | Priority |
|------|-------------|----------|
| Fresh-machine installation test | Bootstrap on clean macOS + Ubuntu | P0 |
| Performance benchmark suite | Automated benchmarks | P1 |
| Security audit (final) | Address all OPEN findings | P1 |
| Demo dataset | Anonymized sample corpus for testing | P2 |
| GitHub release | v1.0.0 with release notes | P0 |

**Sprint 3 Exit Criteria:**
- [ ] Fresh install works on macOS and Ubuntu
- [ ] All documentation current and accurate
- [ ] Security audit has 0 OPEN/HIGH findings
- [ ] v1.0.0 tagged and released

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Test coverage target not met | Medium | Medium | Prioritize critical paths over 100% coverage |
| Docker build issues on ARM64 | Low | Medium | Test multi-arch build early (Week 5) |
| API cost increase during testing | Low | Low | Use test fixtures, not live API calls |
| Fly.io deployment complexity | Medium | Medium | Document fallback to Docker self-hosted |

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Roadmap completion | 95%+ (223/235 tasks) | Task tracking |
| Test coverage | 80%+ | `npm run test:coverage` |
| Search relevance (MRR@10) | > 0.7 | Automated benchmark |
| API response time (p99) | < 200ms | Performance test |
| Fresh install time | < 10 minutes | Manual verification |

## Related Documents

- `DEVELOPMENT_ROADMAP.md` -- Full 235-item task list
- `07_DEPLOYMENT_GUIDE.md` -- Deployment procedures
- `benchmark-report.md` -- Performance baselines
- `05-vulnerability-audit.md` -- Security findings to address
