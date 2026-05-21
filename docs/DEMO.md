# Recording a demo GIF (optional)

The README uses **PNG screenshots** so the repo stays lightweight. To add a GIF:

1. Start the stack: `docker compose up --build` (or dev API + web).
2. Open http://localhost:8080 and search **BRCA1**.
3. Open the gene detail page — show the force-directed graph pan/zoom.
4. Record 10–20 seconds with [ScreenToGif](https://www.screentogif.com/) or OBS.
5. Save as `docs/demo-walkthrough.gif` and add to README:

   ```markdown
   ![Demo walkthrough](docs/demo-walkthrough.gif)
   ```

No application code changes are required.
