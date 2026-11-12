# AI-Assisted Software Testing Report

**Student Name:** ______________________________  
**Date:** ____________________

This is an individual report based on your own Week 3 RAG chatbot.


## 1. Requirements and Test Oracle
- What behaviors did you decide were required?
- What source material was used as ground truth?

## 2. AI-Generated Test Cases
- Which tests came from requirements?
- Which tests were suggested by AI?
- Which AI suggestion relied on an invented assumption?

## 3. Functional Test Results
- Number passed / failed: 12 passed / 0 failed (pytest -v, freshly rerun) 
- Most important failure:None in the current test run. The high cold-start latency is the main issue to monitor, not a functional test failure

## 4. Performance Results
- Min / average / median / max latency:  0.01s / 3.14s / 0.01s / 31.23s 
Failed requests: 0 of 10
- Proposed target and justification: warm median under 1s, p95 under 3s, and zero failures. This is reasonable given the 0.01–0.02s warm averages in the concurrency test. Track cold startup separately: its roughly 27–31s latency dominates the benchmark average and maximum.

## 5. Stress / Concurrency Results
- What changed at 1, 3, and 5 simultaneous requests?  request: 1/1 succeeded; average 27.18s (cold-start run) 3 simultaneous requests: 3/3 succeeded; average 0.01s. 5 simultaneous requests: 5/5 succeeded; average 0.02s. No API or rate-limit errors observed; no instability observed.

## 6. User Acceptance Testing
Ask one classmate to test your chatbot for approximately five minutes; record that classmate’s ratings and comments below.
- Relevance rating:
- Correctness rating:
- Clarity rating:
- Trust rating:
- Overall usefulness:
- User comments:

## 7. Failure Analysis
Describe at least three failures or weak outcomes and classify each as retrieval, generation, specification/oracle, weak assertion, hallucinated test scenario, or performance/rate-limit issue.

## 8. Reflection
Would you trust the same model that helps write the chatbot to be the sole generator/judge of its tests? What would you change before production use? 
No, utilizing the model that generated my chatbot to also judge the tests is risky due to systematic biases, inconsistent reasoning, and misaligned evaluation standards. 
