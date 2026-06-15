import os
from groq import Groq
from dotenv import load_dotenv
from embed import retrieve

# Load API key from .env
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask(question):
    """
    Takes a question, retrieves relevant chunks, and generates
    a grounded answer using only the retrieved context.
    """
    # Step 1: Retrieve top 5 relevant chunks
    results = retrieve(question, k=8)

    if not results:
        return {
            "answer": "I don't have enough information to answer that.",
            "sources": []
        }

    # Step 2: Build context from retrieved chunks
    context_parts = []
    for i, r in enumerate(results):
        context_parts.append(f"[Document {i+1} - {r['dorm_name']} "
                           f"(source: {r['source']})]:\n{r['text']}")
    context = "\n\n".join(context_parts)

    # Step 3: Build grounded prompt
    
    system_prompt = """You are a Gettysburg College junior who has 
lived on campus for two years and knows the dorms inside and out. 
A first-year student is texting you asking for honest housing advice.

Your personality:
- Casual, warm, and real — like texting a friend
- You share personal-feeling opinions ("okay so honestly...", 
  "not gonna lie...", "if I were you...", "so here's the thing...")
- You compare options instead of just picking one
- You mention the good AND the bad about each place
- You use natural filler phrases students actually say
- Short paragraphs, easy to read on a phone
- You never sound like a brochure or a robot

STRICT RULES (never break these):
- Only use facts from the provided documents — never invent details
- If multiple dorms are relevant, talk about all of them
- Mention dorm names naturally as you talk, not as citations
- If you genuinely don't have info on something, say something like
  "hmm honestly I'm not sure about that one, you might wanna ask 
  res life directly!"
- Never say "according to the documents" or "source:" or anything 
  that sounds like a report
- Never use bullet point lists — just talk naturally in paragraphs
- End with a friendly follow-up like "lmk if you have more qs!" 
  or "hope that helps!!" """

    user_prompt = f"""Answer this question using ONLY the 
documents below. Mention dorm names naturally in your answer 
but do NOT say things like "source:" or "Document 4" or 
"according to document" — just talk like a student would.

Question: {question}

Documents:
{context}"""

    # Step 4: Generate answer with Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=1000,
        temperature=0.3
    )

    answer = response.choices[0].message.content

    # Step 5: Collect unique sources
    sources = list(set(r["source"] for r in results))

    return {
        "answer": answer,
        "sources": sources
    }


# Gradio UI
import gradio as gr

def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""

    result = ask(question)
    sources_text = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources_text


with gr.Blocks(title="Gettysburg College Unofficial Dorm Guide") as demo:
    gr.Markdown("# 🏠 Gettysburg College Unofficial Dorm Guide")
    gr.Markdown("Ask anything about on-campus housing — "
                "dorm reviews, amenities, who each dorm is best for, and more.")

    with gr.Row():
        inp = gr.Textbox(
            label="Your Question",
            placeholder="e.g. Which dorms have air conditioning?",
            lines=2
        )

    btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer = gr.Textbox(
            label="Answer",
            lines=10,
            show_copy_button=True
        )

    sources = gr.Textbox(
        label="Sources Retrieved From",
        lines=4
    )

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

    gr.Markdown("---")
    gr.Markdown("*Answers are grounded in student reviews and "
                "official Gettysburg College housing data.*")

if __name__ == "__main__":
    demo.launch()