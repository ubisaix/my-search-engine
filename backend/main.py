from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.database import (
    create_table,
    add_document,
    search_documents
)

from backend.crawler import crawl


app = FastAPI(title="My Search Engine API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():

    create_table()

    # საწყისი მონაცემები
    add_document(
        "Wikipedia",
        "https://www.wikipedia.org/",
        "Wikipedia არის თავისუფალი ონლაინ ენციკლოპედია."
    )

    add_document(
        "GitHub",
        "https://github.com/",
        "GitHub არის პროგრამული პროექტების ჰოსტინგის პლატფორმა."
    )

    add_document(
        "Google",
        "https://www.google.com/",
        "Google არის საძიებო და ტექნოლოგიური კომპანია."
    )

    add_document(
        "YouTube",
        "https://www.youtube.com/",
        "YouTube არის ვიდეოების გაზიარების პლატფორმა."
    )


@app.get("/")
def home():

    return {
        "name": "My Search Engine",
        "status": "online",
        "database": "connected"
    }


@app.get("/search")
def search(
    q: str = Query(..., min_length=1)
):

    query = q.strip()

    rows = search_documents(query)

    results = []

    for row in rows:

        results.append({
    "title": title,
    "url": url,
    "description": content[:500],
    "score": score
})

        results.append({
            "title": title,
            "url": url,
            "description": content[:500]
        })

    return {
        "query": query,
        "total": len(results),
        "results": results
    }


@app.get("/crawl")
def crawl_url(
    url: str = Query(..., min_length=8)
):

    if not url.startswith(
        ("http://", "https://")
    ):
        raise HTTPException(
            status_code=400,
            detail="URL must start with http:// or https://"
        )

    links = crawl(url)

    return {
        "url": url,
        "status": "indexed",
        "links_found": len(links)
    }


@app.get("/test")
def test():

    return {
        "message": "MY SEARCH ENGINE API WORKS"
    }
