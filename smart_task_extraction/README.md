# Smart Task Extraction Feature
 
 This folder contains the **Smart Task Extraction** feature, a standalone module for extracting actionable tasks from emails using AI.
 
 ## Implementation Mapping
 
 - Core service implementation:
   - `smart_task_extraction/services/task_extractor.py`
   - Class: `TaskExtractorService`
 
 - API routes (FastAPI):
   - `smart_task_extraction/api/routes_tasks.py`
   - Router prefix: `/api/v1/tasks`
 
 ## Main Endpoints
 
 - `POST /api/v1/tasks/extract` – extract tasks from a single email
 - `POST /api/v1/tasks/extract/batch` – batch task extraction
 - `GET  /api/v1/tasks` – list tasks (with optional filters)
 - `GET  /api/v1/tasks/{task_id}` – get a single task
 - `PATCH /api/v1/tasks/{task_id}` – update a task
 - `PATCH /api/v1/tasks/{task_id}/complete` – mark task complete
 - `GET  /api/v1/tasks/by-email/{email_id}` – tasks from one email
 - `DELETE /api/v1/tasks/{task_id}` – delete a task
 
 ## Notes
 
 - This module shares the database and some models with the `priority_scoring` module but operates independently for task logic.

