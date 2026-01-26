1.0 Tool Identity  
1.1 Name: AliasMaker  
1.2 Role: Create and manage filesystem aliases/links so that one physical file can appear in multiple “views” or projects without duplication.  

2.0 Inputs and Outputs  
2.1 Inputs  
2.1.1 One or more source file paths (e.g., PDFs, images, docs).  
2.1.2 One or more target folders where aliases should appear.  

2.2 Outputs  
2.2.1 Finder aliases (or equivalent links) created in the target folders.  
2.2.2 Optional mapping log for future cleanup or rebuild.  

3.0 Core Behavior  
3.1 Take a mapping of source files → destination folders.  
3.2 For each mapping, create an alias in the destination that points to the source file.  
3.3 Never move or duplicate the original file; only create references.  
3.4 Optionally skip alias creation if one already exists and is valid.  

4.0 Constraints and Guarantees  
4.1 AliasMaker is not allowed to delete or overwrite real source files.  
4.2 AliasMaker should be safe to re-run: duplicates are not created when an alias already exists.  
4.3 AliasMaker is intended as infrastructure for organizing knowledge views (projects, cases, bots, and automations) without breaking canonical storage.  
4.4 AliasMaker should keep a machine-readable record of mappings so future agents can rebuild or refactor alias trees without manual intervention.  
