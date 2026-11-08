# Testing Report: Required Reflection Questions

## 1. Which tests came directly from the known requirements, and which were suggested by AI?

The requirement-based factual tests, which check correctness against known answers in the documents, came directly from the known requirements. The ambiguous question, which could match several documents, was suggested by AI.

## 2. Which AI-generated test case was most useful? Which was least useful or based on an invented assumption?

The most useful AI-generated test was the adversarial question. It was designed to expose limitations and vulnerabilities in the chatbot, so it revealed how the system behaves at its edges.

The least useful was the ambiguous question. It has no standard answer, so there is technically no wrong response. Any reasonable answer could be accepted, which made the result subjective and hard to evaluate.

## 3. Did you encounter a case where a test passed even though the chatbot answer was not actually good?

Yes. On one factual question, the chatbot gave more detail than was needed. The expected answer was a single percentage, but the chatbot returned several supporting sentences that contained the correct number. The test passed because the number was present, even though the answer was wordier than it should have been.

## 4. What were the most common failure modes?

The most common failure modes were **specification/oracle** problems and **performance** problems. Specification/oracle issues came from tests whose expected answers were unclear or too loose. Performance issues came mainly from the slow first request.

## 5. How did latency change as workload increased?

As concurrency increased, warm-request latency barely changed. Average latency was 0.01s at 3 concurrent requests and 0.02s at 5. The single-request run took 27.18s, which was likely a cold-start or indexing delay, so it is not a fair comparison with the warm runs.

## 6. What did the UAT tester notice that the automated tests did not?

The UAT tester noticed that the chatbot's answers were sometimes wordier than necessary. The automated tests only checked for the presence of key facts, so they did not catch this.

## 7. Would you trust the same model that helps write the chatbot to be the sole generator and judge of its tests?

No. Using the same model to build the chatbot and to generate and judge its tests is risky. It can share the same systematic biases and blind spots, reason inconsistently, and apply evaluation standards that don't match the real requirements. Independent human review, or a different model, gives a more reliable check.

## 8. What would you change before calling this chatbot production-ready?

I would improve the specification/oracle and the performance of the RAG system so that its answers are clear, correct, and delivered reliably.

**Why the current results are not enough**
- A real RAG answer needs retrieval plus LLM generation, which takes seconds. The very fast warm responses suggest caching or repeated questions.
- Concurrency of 1, 3, and 5 is too small. Passing at 5 simultaneous requests says little about 20 or 50 users.
- The 12 functional tests passed. That shows correctness, not performance, and it does not prove the fast answers are right.

**Changes to make**

1. **Fix the cold start (highest priority).**
   - Load the model, embeddings, and vector index at startup, not on the first request.
   - Add a warm-up request when the app starts, and a readiness check so traffic is sent only when the app is ready.
   - Keep at least one instance warm if the app is hosted on a platform that scales to zero.

2. **Verify the fast responses are real.**
   - Check whether caching is on, and whether the benchmark repeats the same question.
   - Rerun with varied, uncached questions and confirm the answer text is correct and not empty or canned.
   - Run the key-fact checks on every response under load, not just on HTTP success.

3. **Measure properly.**
   - Report p50, p95, and p99, and report cold and warm runs separately.
   - Use hundreds of requests, not 10.
   - Test higher concurrency (10, 25, 50) until latency or errors change, to find the real limit.
   - Include long and multi-document questions.

4. **Set targets and enforce them.**
   - Agree on a target, such as p95 under a stated number of seconds with at least 99% success.
   - Add timeouts on each stage and an overall deadline.
   - Add a fallback, such as a short "try again" message, so no request waits 30 seconds.
   - Cap retries, context size, and output tokens.

5. **Check external limits.** With few and cached requests, the LLM provider's rate limits have not been tested. Try uncached traffic at higher concurrency, and plan for backoff and queueing.

6. **Add monitoring.** Track latency percentiles, error rate, timeouts, and cache hit rate in production so problems are visible.
