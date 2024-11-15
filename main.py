from fastapi import FastAPI, Request
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlencode
from v1.router import router
import nest_asyncio  # type: ignore
nest_asyncio.apply()

app = FastAPI()
frontend_url = "https://stockbot-frontend.vercel.app"
origins = [frontend_url]
# origins = ["https://stockbot-frontend.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicitly list allowed methods
    allow_headers=["*"],
    expose_headers=["*"],  # Add this if you need to expose any headers to the frontend
    max_age=3600,  # Cache preflight requests for 1 hour
)
app.include_router(router)

# @app.middleware("http")
# async def flatten_query_string_lists(request: Request, call_next):
#     flattened: list[tuple[str, str]] = []
#     for key, value in request.query_params.multi_items():
#         flattened.extend((key, entry) for entry in value.split(","))

#     request.scope["query_string"] = urlencode(flattened, doseq=True).encode("utf-8")

#     return await call_next(request)

@app.middleware("http")  # Changed from "https" to "http"
async def flatten_query_string_lists(request: Request, call_next):
    flattened: list[tuple[str, str]] = []
    for key, value in request.query_params.multi_items():
        flattened.extend((key, entry) for entry in value.split(","))
    request.scope["query_string"] = urlencode(flattened, doseq=True).encode("utf-8")
    response = await call_next(request)
    
    # Add CORS headers to the response
    response.headers["Access-Control-Allow-Origin"] = frontend_url
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

@app.get("/health")
def health():
    return {"status": "ok"};


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5001,
        reload= True,
    )
    
