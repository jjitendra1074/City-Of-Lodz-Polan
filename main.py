from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from upload import router as upload_router
from hybrid_search import hybrid_search
from reranker import rerank
from llm import ask_llm
from fastapi.responses import HTMLResponse


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # allow all origins
    allow_credentials=True,
    allow_methods=["*"],            # allow all methods (GET, POST, PUT, DELETE, OPTIONS, ...)
    allow_headers=["*"],            # allow all headers
)

app.include_router(upload_router)


@app.post("/chat")
def chat(payload: dict):

    query = payload["query"]

    retrieved = hybrid_search(query)

    print("-------------------------------")
    print(retrieved)
    print("-------------------------------")

    reranked = rerank(query, retrieved)

    print("-------------------------------")
    print(reranked)
    print("-------------------------------")

    context = "\n\n".join([
        f"Clause: {chunk.clause}\n{chunk.content}"
        for chunk in reranked
    ])

    answer = ask_llm(query, context)

    sources = []

    for chunk in reranked:
        sources.append({
            "document": chunk.document_name,
            "clause": chunk.clause,
            "page": chunk.page
        })

    return {
        "answer": answer,
        "sources": sources
    }

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legal Hybrid RAG Chatbot</title>

    <style>

        body {
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            font-family: Arial, sans-serif;
        }

        .container {
            width: 90%;
            max-width: 1000px;
            margin: 30px auto;
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
        }

        h1 {
            text-align: center;
        }

        .section {
            margin-top: 30px;
        }

        textarea {
            width: 100%;
            height: 120px;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ccc;
            resize: vertical;
            font-size: 15px;
        }

        button {
            margin-top: 15px;
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 15px;
        }

        button:hover {
            background-color: #0056b3;
        }

        .status {
            margin-top: 15px;
            font-weight: bold;
        }

        .chat-box {
            margin-top: 30px;
        }

        .message {
            margin-bottom: 25px;
            padding: 15px;
            border-radius: 8px;
        }

        .question {
            background-color: #eef5ff;
        }

        .answer {
            background-color: #f1fff1;
        }

        .sources {
            margin-top: 15px;
            background: #fafafa;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 5px;
        }

        .source-item {
            margin-bottom: 10px;
        }

        #loading {
            display: none;
            color: green;
            margin-top: 10px;
        }

    </style>
</head>

<body>

<div class="container">

    <h1>Legal Hybrid RAG Chatbot</h1>

    <!-- Upload Section -->
    <div class="section">

        <h2>Upload Legal Document</h2>

        <input type="file" id="pdfFile" accept=".pdf">

        <br>

        <button onclick="uploadDocument()">
            Upload Document
        </button>

        <div class="status" id="uploadStatus"></div>

    </div>

    <hr>

    <!-- Chat Section -->
    <div class="section">

        <h2>Ask Legal Question</h2>

        <textarea
            id="questionInput"
            placeholder="Example: Can employer terminate contract without notice?"
        ></textarea>

        <br>

        <button onclick="askQuestion()">
            Ask Question
        </button>

        <div id="loading">
            Processing question...
        </div>

        <div class="chat-box" id="chatBox"></div>

    </div>

</div>

<script>

const API_BASE = " https://untreadable-balkiest-tony.ngrok-free.dev";


// Upload PDF
async function uploadDocument() {

    const fileInput = document.getElementById("pdfFile");
    const uploadStatus = document.getElementById("uploadStatus");

    if (fileInput.files.length === 0) {
        alert("Please select a PDF file.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    uploadStatus.innerText = "Uploading document...";

    try {

        const response = await fetch(`${API_BASE}/upload`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        uploadStatus.innerText =
            `Upload successful. Chunks created: ${data.chunks}`;

    } catch (error) {

        console.error(error);
        uploadStatus.innerText = "Upload failed.";
    }
}


// Ask Question
async function askQuestion() {

    const questionInput = document.getElementById("questionInput");
    const question = questionInput.value.trim();

    const loading = document.getElementById("loading");
    const chatBox = document.getElementById("chatBox");

    if (!question) {
        alert("Please enter a legal question.");
        return;
    }

    loading.style.display = "block";

    try {

        const response = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                query: question
            })
        });

        const data = await response.json();

        const messageDiv = document.createElement("div");

        messageDiv.innerHTML = `

            <div class="message question">
                <strong>Question:</strong>
                <p>${question}</p>
            </div>

            <div class="message answer">
                <strong>Answer:</strong>
                <p>${data.answer}</p>

                <div class="sources">
                    <strong>Sources:</strong>

                    ${
                        data.sources.map(source => `
                            <div class="source-item">
                                <strong>Document:</strong> ${source.document}<br>
                                <strong>Clause:</strong> ${source.clause}<br>
                                <strong>Page:</strong> ${source.page}
                            </div>
                        `).join('')
                    }

                </div>
            </div>
        `;

        chatBox.prepend(messageDiv);

        questionInput.value = "";

    } catch (error) {

        console.error(error);
        alert("Error while processing question.");

    } finally {

        loading.style.display = "none";
    }
}

</script>

</body>
</html>
    """
