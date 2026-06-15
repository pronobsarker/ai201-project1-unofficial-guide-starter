---

## Embedding Model

** Model used:** all-MiniLM-L6-v2 via sentence-transformers  
**Runs:** Fully locally, no API key or rate limits required

**Production tradeoff reflection:**  
For a real deployment I would consider:
- **Accuracy:** all-MiniLM-L6-v2 is trained on general text. 
  OpenAI's text-embedding-3-small would likely produce stronger 
  semantic matches for domain-specific housing language.
- **Context length:** all-MiniLM-L6-v2 caps at 256 tokens, 
  which fits our short review chunks well. Longer documents 
  would need a higher token limit model.
- **Cost:** sentence-transformers runs free locally. API-based 
  embeddings add per-request cost at scale.
- **Latency:** Local models add startup time but have zero 
  network latency per query.

---

## Retrieval Test Results

**Query 1:** "Which dorms have air conditioning?"  
Top chunks returned:
- Hanson Hall — REVIEW 1 (mentions central AC)
- West Hall — PROS (mentions central AC)
- Colonial Hall — PROS (mentions individual AC units)

These chunks are relevant because each explicitly mentions 
air conditioning as a feature of that specific dorm.

**Query 2:** "What dorm is best for making friends as a 
first year?"  
Top chunks returned:
- Patrick Hall — BEST FOR (social, academically integrated)
- Hanson Hall — REVIEW 3 (lively, collaborative atmosphere)
- Musselman Hall — BEST FOR (central location, upperclassmen)

Patrick and Hanson are directly relevant. Musselman is 
partially relevant — it's social but aimed at upperclassmen, 
so the LLM correctly deprioritized it in the response.

**Query 3:** "What are the complaints about Musselman Hall?"  
Top chunks returned:
- Musselman Hall — CONS (no elevator, overheating, lottery)
- Musselman Hall — REVIEW 3 (overheating on 4th floor)
- Musselman Hall — REVIEW 2 (stressful housing lottery)

All three chunks are directly relevant — this was the 
strongest retrieval result in testing.

---

## How Grounded Generation is Enforced

Grounding is enforced in two ways:

**1. System prompt instruction:**  
The LLM is explicitly told: "Only use facts from the provided 
documents — never invent details." It is also told to say 
"I don't have good info on that one" if the topic isn't 
covered.

**2. Pipeline structure:**  
The LLM only receives retrieved chunks as context — it has 
no access to external search or its general training 
knowledge about Gettysburg College specifically. Every answer 
is generated from what was retrieved.

---

## Example Responses

**Example 1 — Question with good retrieval:**

*Question:* What are the complaints about Musselman Hall?

*Answer:* So I've lived on campus for a bit, and I've gotta 
say, Musselman Hall is a popular spot but it's got some real 
downsides. One of the main complaints is that it lacks an 
elevator, which can be a real pain if you're on the upper 
floors. Not gonna lie, it's also prone to overheating on 
those upper floors during winter and autumn. And the housing 
lottery process can be super stressful due to high demand. 
Lmk if you have more qs!

*Sources retrieved from:* musselman_hall_reviews.txt

**Example 2 — Out-of-scope question (refusal):**

*Question:* What is the food like at the dining hall?

*Answer:* Hmm honestly I don't have good info on that one — 
my knowledge is mainly about the dorms and housing stuff. 
You might wanna ask res life or check out the dining services 
page directly! Lmk if you have more qs about housing though!

---

## Query Interface

**Input:** A text box labeled "Your Question" with a 
placeholder example. Press Enter or click "Ask" to submit.

**Output:**  
- "Answer" field — conversational response from the LLM 
  grounded in retrieved documents  
- "Sources Retrieved From" field — lists the .txt filenames 
  the answer was drawn from

**Sample interaction:**

> *Input:* Which dorms have elevators or ADA accessibility?
>
> *Answer:* So here's the thing, if you're looking for dorms 
> with elevators or ADA accessibility, Haaland Hall and Huber 
> Hall are your best bets. Haaland Hall has an elevator and 
> is fully ADA-compliant. Huber Hall also has elevator access. 
> Some dorms like Patrick Hall and College Apartments lack 
> elevators entirely, so keep that in mind!
>
> *Sources:* haaland_hall_reviews.txt, huber_hall_reviews.txt

---

## Evaluation Report

| # | Question | Expected Answer | System Response | Accuracy |
|---|----------|-----------------|-----------------|----------|
| 1 | Which dorms have air conditioning? | Hanson, Huber, Patrick, Musselman, Rice, Stine all have AC | Correctly named Colonial, Hanson, West Hall, College Apartments as having AC — missed a few but factually correct on those mentioned | Partially Accurate |
| 2 | What dorm is best for a first-year student who wants to make friends quickly? | Hanson Hall and Patrick Hall | Correctly identified both Patrick and Hanson, explained the difference between them | Accurate |
| 3 | Which dorms have elevators or ADA accessibility? | Huber Hall and Haaland Hall | Correctly identified both Haaland and Huber, also correctly named several dorms that lack elevators | Accurate |
| 4 | What are the main student complaints about Musselman Hall? | Overheating, no elevator, competitive lottery | Correctly named all three main complaints with good detail | Accurate |
| 5 | What should I know about laundry at Gettysburg College? | Pay-per-use, costs $100+/semester, some buildings better than others | Correctly described the laundry situation across multiple dorms, mentioned off-site laundry issues | Accurate |

---

## Failure Case

**Question 1 — Which dorms have air conditioning?** was 
partially accurate. The system correctly named dorms that 
have AC but missed several (Huber, Patrick, Stine, Rice) 
that are also explicitly mentioned as having AC in the 
documents.

**Why it happened:** The retrieval step returned only 8 
chunks (k=8), and with 20+ dorms having AC mentioned across 
47 files, not all relevant chunks made it into the top 8 
results. The embedding model ranked some chunks higher based 
on semantic similarity even when other equally relevant 
chunks existed further down. This is a retrieval coverage 
problem — increasing k would surface more dorms but also 
risk diluting the context with less relevant material.

---

## Spec Reflection

**One way the spec helped:** Writing the chunking strategy 
in planning.md before coding forced me to think about what 
each chunk needs to contain on its own. The decision to 
prepend the dorm name to every chunk came directly from 
writing the spec — I realized during planning that a PROS 
chunk saying "Full central air conditioning" with no dorm 
name attached would be useless to the LLM.

**One way implementation diverged:** The planning.md assumed 
chunk sizes of ~300 characters with overlap. In practice, 
splitting by section label produced variable-length chunks 
(some REVIEW chunks are 150 characters, some PROS sections 
are 400+). This worked better than fixed-size splitting for 
this document structure, but it meant the overlap strategy 
became less relevant since section boundaries were natural 
stopping points.

---

## AI Usage

**Instance 1 — ingest.py:**  
I gave Claude my chunking strategy section from planning.md 
and one sample .txt file. I asked it to write a script that 
splits by section label and prepends the dorm name. Claude 
produced a working script. I reviewed and kept it largely 
as generated because it matched my spec exactly and produced 
231 clean chunks when tested.

**Instance 2 — System prompt tone:**  
The initial system prompt Claude wrote produced stiff, 
formal answers that sounded like a brochure. I directed 
Claude to rewrite it to sound like a Gettysburg junior 
texting a friend, specifying phrases like "not gonna lie" 
and "lmk if you have more qs." I also added the rule 
"never use bullet point lists" after seeing the first 
responses use them. The final tone came from several rounds 
of my direction, not just the initial generation.