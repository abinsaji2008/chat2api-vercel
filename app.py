import warnings
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer
from utils.configs import api_prefix
warnings.filterwarnings("ignore")
app = FastAPI(docs_url=f"/{api_prefix}/docs" if api_prefix else "/docs", redoc_url=f"/{api_prefix}/redoc" if api_prefix else "/redoc", openapi_url=f"/{api_prefix}/openapi.json" if api_prefix else "/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
templates = Jinja2Templates(directory="templates")
security_scheme = HTTPBearer(auto_error=False)
@app.get("/health")
async def health():
    from utils.configs import chatgpt_cookies
    return {"status":"ok","cookie_configured":bool(chatgpt_cookies)}
import api.chat2api
@app.api_route("/" + (api_prefix + "/" if api_prefix else "") + "{path:path}", methods=["GET","POST","PUT","DELETE","OPTIONS","HEAD","PATCH","TRACE"])
async def fallback(path: str):
    raise HTTPException(status_code=404, detail="Not found")
