# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
On-campus dormitory reviews and student housing experiences at 
Gettysburg College. This knowledge is valuable because the official 
college housing pages only list room dimensions and amenities — they 
never tell you that Musselman's 4th floor overheats, that Hanson has 
thin walls, or which dorm actually has reliable laundry machines. 
Students currently have no single searchable resource for this; they 
rely on asking upperclassmen or stumbling across scattered forum posts.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->


47 .txt files collected via Gemini Deep Research, compiled from 
multiple student-facing sources. Each file covers one dorm and 
follows a consistent structure: DORM / SOURCE / REVIEW 1-3 / 
PROS / CONS / BEST FOR.

| #  | Source                              | Description                        | URL or location           |
|----|-------------------------------------|------------------------------------|---------------------------|
| 1  | Roomsurf.com                        | Student dorm ratings and reviews   | roomsurf.com              |
| 2  | The Gettysburgian                   | Student newspaper housing articles | gettysburgian.com         |
| 3  | Gettysburg College Residential Ed   | Official dorm descriptions         | gettysburg.edu/housing    |
| 4  | WordPress Huber Hall History        | Student-written dorm history       | Local file                |
| 5  | Niche.com                           | Student reviews of campus housing  | niche.com                 |
| 6  | College Confidential                | Forum threads about Gettysburg     | collegeconfidential.com   |
| 7  | Unigo.com                           | Student experience reviews         | unigo.com                 |
| 8  | Reddit r/GettysburgCollege          | Student discussions about housing  | reddit.com                |
| 9  | Gettysburg College structured data  | Room type and feature data         | gettysburg.edu            |
| 10 | Gemini Deep Research synthesis      | Compiled and paraphrased reviews   | Local .txt files          |

Dorms covered: Hanson Hall, Huber Hall, Patrick Hall, Musselman Hall,
Paul Hall, Stevens Hall, Penn Hall, McKnight Hall, and others.

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 300 characters
**Overlap:** 50 characters
**Reasoning:**
Each .txt file has clearly labeled sections: REVIEW 1, REVIEW 2, 
REVIEW 3, PROS, CONS, and BEST FOR. Each section answers a different 
type of question, so each section becomes its own chunk.

- REVIEW chunks answer: "What do students say about living here?"
- PROS/CONS chunks answer: "What are the tradeoffs of this dorm?"
- BEST FOR chunks answer: "Who should choose this dorm?"

Keeping sections as separate chunks means a query about noise will 
retrieve the CONS chunk specifically, not a diluted mix of everything.

Reviews are 2-4 sentences, so 300 characters fits one complete 
thought without cutting it off. Overlap of 50 characters protects 
against edge cases where a thought spans a section boundary.

Every chunk will be prefixed with the dorm name during ingestion 
(e.g., "Hanson Hall — CONS: thin walls...") so the LLM always knows 
which dorm a chunk refers to, even without surrounding context.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers
**Top-k:** 5 chunks per query

**Production tradeoff reflection:**
For a real deployment I would consider:

- **Accuracy:** all-MiniLM-L6-v2 is fast and free but trained on 
  general text. For domain-specific housing language, OpenAI's 
  text-embedding-3-small would likely produce better semantic matches.

- **Context length:** all-MiniLM-L6-v2 caps at 256 tokens, which 
  fits our short review chunks well. Longer documents would need 
  a model with a higher token limit.

- **Cost:** sentence-transformers runs fully locally with no API 
  cost or rate limits, which is ideal for a student project. In 
  production, API-based embeddings add per-request cost at scale.

- **Latency:** Local models add startup time but have no network 
  latency per query. For a high-traffic app, a hosted API might 
  actually be faster.

Top-k of 5 gives the LLM enough context to compare 1-2 dorms on a 
specific topic without flooding it with loosely related chunks from 
unrelated dorms.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected Answer |
|---|----------|-----------------|
| 1 | Which dorms at Gettysburg College have air conditioning? | Hanson Hall, Huber Hall, Patrick Hall, and Musselman Hall all have central AC mentioned in their reviews |
| 2 | What dorm is best for a first-year student who wants to make friends quickly? | Hanson Hall (described as "exceptionally social") and Patrick Hall (seminar-based community) |
| 3 | Which dorms have elevators or ADA accessibility? | Huber Hall is explicitly ADA-compliant with an elevator; Patrick Hall explicitly lacks one |
| 4 | What are the main student complaints about Musselman Hall? | Overheating on upper floors, no elevator, highly competitive housing lottery |
| 5 | What should I know about Hanson Hall bathrooms? | Basement floor has larger communal bathrooms but periodic plumbing issues (clogs, drainage delays) |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Dorm name missing from retrieved chunks:** If we split by 
   section, a PROS chunk might just read "Full central air 
   conditioning" with no dorm name attached. The retrieval system 
   would return it, but the LLM wouldn't know which dorm it 
   describes. Fix: prepend dorm name to every chunk at ingestion 
   time (e.g., "Musselman Hall — PROS: Full central air 
   conditioning...").

2. **AI-synthesized content vs. real quotes:** Our documents were 
   compiled by Gemini Deep Research, which paraphrases rather than 
   copying verbatim student quotes. This means some details could 
   be inaccurate or blended across sources. We will note this 
   limitation honestly in the README and flag it as a known 
   weakness in the evaluation report.
---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

[Document Ingestion]        [Chunking]              [Embedding + Vector Store]
 Load 47 .txt files    →   Split by section    →    all-MiniLM-L6-v2
 Python / os.listdir        label (REVIEW,           sentence-transformers
                            PROS, CONS,              stored in ChromaDB
                            BEST FOR)                with source metadata
                            Prepend dorm name
                                                            ↓
                                                    [Retrieval]
                                                    top-5 chunks by
                                                    semantic similarity
                                                            ↓
                                                    [Generation]
                                                    Groq API
                                                    llama-3.3-70b-versatile
                                                    grounded prompt
                                                            ↓
                                                    [Gradio UI]
                                                    Text input box
                                                    Answer display
                                                    Sources display
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
Tool: Claude
Input: My Chunking Strategy section + one sample .txt file 
       (hanson_hall_reviews.txt) + the requirement to prepend 
       dorm name to every chunk
Expected output: An ingest.py script that loads all .txt files 
       from a /data folder, splits each file by section label 
       (REVIEW 1, PROS, CONS, BEST FOR), prepends the dorm name 
       to each chunk, and returns a list of dictionaries with 
       keys: text, source, dorm_name
Verification: Print 5 random chunks and confirm each one is 
       readable, contains a dorm name, and is self-contained

**Milestone 4 — Embedding and retrieval:**
Tool: Claude
Input: My Retrieval Approach section + the chunk dictionary 
       format from Milestone 3 + pipeline diagram
Expected output: An embed.py script that embeds all chunks using 
       all-MiniLM-L6-v2, stores them in ChromaDB with source and 
       dorm_name as metadata, and a retrieve() function that 
       accepts a query string and returns top-5 chunks with 
       their source filenames
Verification: Run 3 test queries from my evaluation plan and 
       confirm returned chunks visibly relate to the question

**Milestone 5 — Generation and interface:**
Tool: Claude
Input: My grounding requirement (answers from retrieved context 
       only), desired output format (answer + source list), 
       and the Gradio structure from the project instructions
Expected output: An app.py that connects retrieval to Groq's 
       llama-3.3-70b-versatile, enforces grounding via system 
       prompt, appends source filenames to every response, and 
       displays results in a Gradio UI with input box, answer 
       field, and sources field
Verification: Ask a question not covered by documents and 
       confirm the system says it doesn't have enough 
       information rather than hallucinating
