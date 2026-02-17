# ChromaDB Compatibility Issue

## Problem
ChromaDB 1.5.0 has compatibility issues with Python 3.14 due to Pydantic v1 dependencies.

## Error
```
pydantic.v1.errors.ConfigError: unable to infer type for attribute "chroma_server_nofile"
```

## Solutions

### Option 1: Use Python 3.11-3.13 (Recommended)
```bash
# Install Python 3.13 or earlier
# Then install ChromaDB
pip install chromadb
```

### Option 2: Use Fallback Mode (Current)
The application automatically falls back to in-memory storage when ChromaDB is unavailable.

```
Warning: ChromaDB not available. Using fallback in-memory storage.
```

This works fine for development and testing, but data won't persist between restarts.

### Option 3: Wait for ChromaDB Update
Monitor ChromaDB releases for Python 3.14 compatibility:
https://github.com/chroma-core/chroma/issues

## Current Status
✅ ChromaDB installed but not functional with Python 3.14
✅ Application runs successfully with fallback mode
✅ All features work except persistent vector storage
