from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="My Search Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

documents = [
    {
        "title": "Wikipedia",
        "url": "https://www.wikipedia.org/",
        "text": "Wikipedia არის თავისუფალი ონლაინ ენციკლოპედია."
    },
    {
        "title": "GitHub",
        "url": "https://github.com/",
        "text": "GitHub არის პროგრამული პროექტების ჰოსტინგის პლატფორმა."
    },
    {
        "title": "Google",
        "url": "https://www.google.com/",
        "text": "Google არის საძიებო და ტექნოლოგიური კომპანია."
    },
    {
        "title": "YouTube",
        "url": "https://www.youtube.com/",
        "text": "YouTube არის ვიდეოების გაზიარების პლატფორმა."
    }
]


@app.get("/")
def home():
    return {
        "name": "My Search Engine",
        "status": "online"
    }


@app.get("/search")
def search(q: str = Query(..., min_length=1)):

    query = q.lower().strip()

    results = []

    for document in documents:

        content = (
            document["title"] + " " +
            document["text"]
        ).lower()

        if query in content:

            results.append({
                "title": document["title"],
                "url": document["url"],
                "description": document["text"]
            })

    return {
        "query": q,
        "total": len(results),
        "results": results
    }
@app.get("/test")
def test():
    return {
        "message": "MY SEARCH ENGINE API WORKS"
    }
