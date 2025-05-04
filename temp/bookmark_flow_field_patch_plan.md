# Patch Plan: Robust Handling of Missing Fields in :bookmark: Flow

## Principles
- Never assume a field is present—always use `.get()` or attribute checks with a default fallback.
- Preserve all existing data—do not overwrite or backfill unless necessary.
- Do not change DB schema or file formats—only adjust how data is read and written.

---

## Where to Apply the Change

### A. When Reading Data (from DB, dict, or file)
- Use `.get("field", "Unknown")` or similar for all fields: `author`, `space_key`, `date_pulled_from_confluence`, etc.
- When reading from SQLAlchemy models, use `getattr(page, "author", "Unknown")` or `page.author or "Unknown"`.

### B. When Writing Data (to DB or file)
- When constructing dicts for DB or file storage, always provide a default if the source value is missing or `None`.
- When parsing files, handle both snake_case and camelCase keys (e.g., `date_pulled_from_confluence` and `datePulledFromConfluence`).

### C. In Embedding/Vectorization Logic
- When constructing the text to embed, always use the fallback logic for all fields.

---

## Specific Code Locations

| File/Module                          | Change Type         | What to Change                        |
|--------------------------------------|---------------------|---------------------------------------|
| database/page_manager.py             | Read/Write fallback | Use `.get()` with defaults            |
| vector/chroma.py                     | Read fallback       | Use `getattr`/`.get()` with defaults  |
| use_cases/vectorize_page.py          | Read fallback       | Use `.get()` with defaults            |
| confluence_integration/store_page_local.py | Write fallback      | Ensure all fields present in dict     |
| confluence_integration/retrieve_space.py   | Write fallback      | Ensure all fields present in dict     |

---

## Example Patch (Pseudocode)
```python
# When reading from a dict
author = page_info.get("author", "Unknown")
space_key = page_info.get("space_key", page_info.get("spaceKey", "Unknown"))
date_pulled_from_confluence = (
    page_info.get("date_pulled_from_confluence") or
    page_info.get("datePulledFromConfluence") or
    datetime.now(timezone.utc)
)

# When reading from a SQLAlchemy model
author = getattr(page, "author", None) or "Unknown"
space_key = getattr(page, "space_key", None) or "Unknown"
```

---

## Testing and Validation
- Test embedding and vectorization for:
  - A newly pulled page from Confluence.
  - An existing page in the DB with missing fields.
- Check logs for any remaining KeyErrors or missing data warnings.
- Confirm that no data is lost or overwritten.

---

## Rollback Plan
- These changes are non-destructive and only affect how data is read/written.
- If any issues arise, revert the fallback logic to the previous direct access. 