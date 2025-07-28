import os
import uvicorn
from api import app

if __name__ == "__main__":
    # Use PORT environment variable if available (for Render), otherwise default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)
