# Optional XHarness WordCraft adapter 0.1.0
Experimental opt-in integration; not an ArtCraft or ZCode product or endorsement.
Requires XHarness optional-panel support and an existing Node.js runtime. Nothing
is installed or enabled automatically. Python remains the normal document path.
Install, explicitly allow MCP, choose full access for the intended session, then
open a workspace DOCX with Edit with WordCraft. The package cannot grant access.
AI editing requires a visible, ready editor. Hiding retains unsaved state but
blocks new model operations. If hidden during an operation, inspect its outcome
once visible; never blindly replay an outcome-unknown edit. Save before closing.
Closing a live operation is rejected. Reload/crash cannot restore unsaved browser
memory: explicit discard is required to reopen a stale editor from the saved file.
Up to two editor panels are retained. The unmodified WASM is 88.45 MB and loads
only after explicit opening. Fonts/page layout can differ from Microsoft Word;
complex DOCX fidelity is not certified. No default enablement or host restart.
All upstream license notices are retained under dist/licenses. This adapter
changes only the transport/bootstrap; the WordCraft engine binary is unchanged.
