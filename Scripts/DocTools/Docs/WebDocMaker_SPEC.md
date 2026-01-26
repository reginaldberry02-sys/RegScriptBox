1.0 Tool Identity  
1.1 Name: WebDocMaker  
1.2 Role: Fetch and normalize web documents (PDFs and text) into canonical storage for LifeOS and BAWS.  

2.0 Inputs and Outputs  
2.1 Inputs  
2.1.1 One or more source URLs (typically HTTPS).  
2.1.2 Optional output folder override (otherwise use the default WebDocs storage path).  

2.2 Outputs  
2.2.1 Downloaded PDF files saved to the canonical WebDocs folder.  
2.2.2 Optional text or Markdown extraction saved alongside the PDF.  

3.0 Core Behavior  
3.1 For each URL, attempt to resolve and download the primary document (usually a PDF).  
3.2 Ensure filenames are deterministic and repeatable (same URL ⇒ same normalized filename).  
3.3 Optionally extract text from PDFs into .md or .txt for later crawling by agents and bots.  
3.4 Log successes and failures so future automations can retry failed URLs only.  

4.0 Constraints and Guarantees  
4.1 WebDocMaker must be idempotent: re-running on the same URL should not create duplicate files, only overwrite or skip according to configuration.  
4.2 WebDocMaker must never silently discard a failed URL; failures are logged with reason.  
4.3 WebDocMaker is read-only with respect to remote sources and write-only into the configured local storage paths.  
4.4 WebDocMaker is a shared infrastructure tool for LifeOS, BAWS, and future agents and must remain backward compatible unless a version bump is explicitly documented.  
