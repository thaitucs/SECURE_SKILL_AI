_quarantine/ - files set aside by SECURE_CHECK
================================================

These files were moved here (not deleted) because you approved the DEL-* items below.
Check that the app still works for a while, then delete this folder yourself.
Do NOT deploy this folder.

LOCAL-ONLY: this folder ignores itself (_quarantine/.gitignore = *) and is listed in
.git/info/exclude. It is never committed or pushed - it exists only on this machine.

To restore a file: move it back to its original path (git tracks it again as before), or
`git checkout <commit-before-change> -- <original path>`.

ID       Original path                     Moved on     Reason / evidence
-------  --------------------------------  -----------  ------------------------------------
DEL-01   {{old/utils_copy.js}}             {{date}}     {{not imported anywhere; duplicate of src/utils.js}}
