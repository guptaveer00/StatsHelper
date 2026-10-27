used codex 

1. Choosing and testing the idea

> I want to build a statistics study helper that finds relevant textbook passages when I describe a confusing concept without knowing its name. Help me decide whether semantic search is appropriate. Ask me questions about what the app should do before suggesting code.

## 2. Inspecting the source


> I want to use Larry Wasserman’s All of Statistics as my starting corpus. Inspect a few actual PDF pages and explain whether the extracted text is readable. Pay attention to equations, headings, and page references. Do not build the whole app yet.


## 3. Writing semantic-search tests before coding

> Help me develop two realistic questions a confused statistics student might ask without using the textbook’s terminology. Identify the passages we expect to retrieve. Treat these as predictions until we test them, and check for important overlapping words.

## 4. Proving persistence

> Help me create the smallest possible ChromaDB persistence test using the current API. Explain PersistentClient and where the data is saved. Run the script twice in separate processes and compare the counts.

## 5. Loading a small real sample


> Implement textbook extraction and load only 50 passages first. Keep page references, measure passage lengths with the embedding model’s tokenizer, and print progress and elapsed time. Explain how rerunning the loader will avoid duplicates.


## 6. Evaluating retrieval honestly

> Run our two proposed questions against the database and show the actual top five results and distances. Also try an unrelated question. Explain which results are useful and which are misleading. Do not call a test successful just because the app returned something.


## 7. Debugging one problem at a time

> The expected passage is missing from the top five. Check whether it was extracted, whether its main explanation was discarded, and whether useful context was embedded or stored only as metadata. Diagnose the cause before changing the code.

## 8. Adding information at runtime

> Add a menu option for saving my own notes while the app is running. Give each note a unique ID, split long notes safely, and let me search the new note immediately. Then verify it remains searchable after restarting.


## 9. Making retrieval useful

> Turn the retrieved passages into a source-based reading guide and recall practice. Keep page references and make every recall answer traceable to the source. Avoid inventing statistical explanations when the text is incomplete.


## 10. Understanding the code

> Walk me through the retrieval function slowly. Explain what gets embedded, how metadata filtering works, why results contain lists of lists, and what the distances mean. Then ask me a few questions so I can check my understanding.


## 11. Final verification

> Test the project from a fresh source-only folder using the README instructions. Check installation, rebuilding the corpus, adding notes, searching, persistence, and saving guides. Confirm that Git excludes the textbook, database, notes, model files, and secrets. Report limitations honestly.

## 12. Documentation and submission

> I wrote the required README sections. Check whether they accurately describe the current code and cover the assignment requirements. Point out missing or misleading statements without replacing my personal writing.
