# Development Context & Methodological Overview

## SDLC Methodology & Implementation Evidence

As specified in the **Task 2 Design Phase**, the overarching methodology for this project is the **Waterfall SDLC**. This ensured a structured progression from requirements analysis and design through to development and testing.

To maximize efficiency during the **Development Phase**, I utilized **Iterative Development** within that stage to proactively discover and resolve bugs. This hybrid approach allowed for high-quality, bug-free deliverables while strictly following the fixed requirements of the college client.

1.  **Iteration 1: Backend Scaffolding & Core Architecture**
    *   **Activity:** Bootstrapped the Flask application alongside foundational Python dictionaries structure (`teams` and `individuals`).
    *   **Refinement Context:** Building purely in-memory data arrays provided robust tracking mechanisms for participants and single-event enforcement without immediately complex database integration holding up iteration throughput.

2.  **Iteration 2: Graphical Display & Component Mapping**
    *   **Activity:** Inherited the approved UX guidelines (custom HTML5/CSS3) and reconstructed them modularly inside Jinja2 view-rendering (`index.html`). 
    *   **Refinement Context:** Early UX observation signaled that loading separate pages for every user action was disorienting. Iterative UI enhancement integrated lightweight ES6 Javascript toggles (`showSection()`) to mask layout views without destructive total-page-reloads.

3.  **Iteration 3: Limit Constraints & Program Robustness Testing**
    *   **Activity:** Fleshed strictly specified business rules (e.g. strict four-team capping, twenty-individual caps, max 5 events) alongside the explicit points schema array (`10-8-6-4-2-1` scale logic).
    *   **Refinement Context:** Attempting 'destructive data testing', such as entering semantic strings like "One" instead of numeric digits inside placement inputs, caused initial processing exceptions halting compiling routing. A `try/except ValueError` block validation boundary was implemented iteratively—elegantly throwing user-level UI warnings via `flash()` alerts instead of triggering HTTP server fatal crashes.

4.  **Iteration 4: Algorithmic Efficiencies**
    *   **Activity:** Evaluating computational loop speed inside calculation components specifically regarding real-time point sorting (`get_leaderboards()`).
    *   **Refinement Context:** I successfully upgraded sorting mechanisms with `operator.itemgetter(1)`. Utilizing this explicit C-built Python Library Routine objectifies the targeted indexing path noticeably faster and cleaner across iterative O(n log n) scales efficiently as data volumes expand.

5.  **Iteration 5: Compliance and Polish Documentation**
    *   **Activity:** Reviewing code line formatting and BTEC project constraints for specific function annotations.
    *   **Refinement Context:** Handled final formatting to assure that every distinct function method natively displayed rigorous descriptive headers demonstrating core variables (Purpose, Inputs, Outputs) consistently, Completing distinction parameters fully.

6.  **Iteration 6: Robustness Refinement & Testing Feedback**
    *   **Activity:** Enhanced the system based on Task 3.3 testing results to address edge cases like ties, data correction, and semantic data integrity.
    *   **Refinement Context:**
        *   *Tie-Breaking:* Switched from simple indexing to a 'Joint Position' algorithm to ensure fairness in leaderboards.
        *   *Data Correction:* Refactored `/record_score` to allow overwriting, enabling users to fix mistakes without data loss.
        *   *Name Integrity:* Added `is_valid_name()` to block purely numeric names like "123", ensuring participants have proper alphabetic identifiers.
        *   *Sanitization:* Hardened input bounds to block unrealistic "extreme" positions (e.g. Rank 99 in a 24-person field) as per Distinction 3.1 requirements.

7. **Iteration 7: Cloud Deployment Architecture**
    *   **Activity:** Configured the repository for Netlify Serverless deployment. 
    *   **Refinement Context:** Restructured paths and added a `serverless-wsgi` handler to ensure the Flask logic translates to a cloud environment correctly.

8. **Iteration 8: Deployment Optimization**
    *   **Activity:** Resolved Netlify "Publish Directory" errors by adjusting the build pipeline.
    *   **Refinement Context:** Modified `netlify.toml` to automatically synthesize a `public` deployment directory during build, ensuring the serverless functions route correctly without static file interference.

9. **Iteration 9: Python Version Stabilization**
    *   **Activity:** Resolved "Definition not found" build errors by leveraging Netlify's default stable Python 3 environment.
    *   **Refinement Context:** Removed restrictive `.python-version` and `runtime.txt` pins that were causing conflicts with the build image's version manager (`mise`), ensuring a smooth dependency installation phase.
