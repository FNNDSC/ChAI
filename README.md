# ChAI - A Natural Language Assistant for ChRIS  [WIP]

<img width="1508" alt="Screenshot 2025-05-08 at 12 48 17 AM" src="https://github.com/user-attachments/assets/03689fef-a69f-417d-a7bf-eecd576abffc" />


This repository sets up a local development environment for the ChAI assistant.

It uses:

- **Ollama** for local LLM inference
- **ChromaDB** (in HTTP server mode) for memory and document storage
- **Streamlit** for the user interface
- **LlamaStack** for agentic related

---

## 🔧 Prerequisites

Before getting started, ensure you have:

- Python **3.11**
- [Ollama](https://ollama.com) installed locally
- [LlamaStack](https://github.com/llama-index/llama-stack) installed
- `streamlit` and `chromadb` installed via pip

---

## 📦 Setup Instructions

### 1. Clone the Repo and Create a Virtual Environment

```bash
git clone https://github.com/YOUR_USERNAME/ChAI
cd ChAI
python3.11 -m venv .chenv
source .chenv/bin/activate
````

---

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

> Ensure your `requirements.txt` includes:
>
> ```text
> chromadb[server]
> streamlit
> llama-stack
> ```

---

### 3. Start the ChromaDB Server Locally

ChromaDB v1.x no longer supports direct Python clients. You must run the Chroma server:

```bash
chroma run --path .chroma_store
```

This starts the ChromaDB server at `http://localhost:8000` and stores data in the `.chroma_store/` folder (acts like a volume).

Leave this terminal running.

---

####

```

podman run \
  --privileged \                                        
  -it \                                                 
  -p 8321:8321 \                                         
  -v ~/.llama/distributions/remote-vllm-milvus/remote-vllm-milvus-run.yaml:/app/config.yaml \ 
                                                        # Mount YAML config into container
  -v /Users/raghurambanda/llama-stack:/app/llama-stack-source \ 
                                                        # Mount local llama-stack source code
  localhost/remote-vllm-milvus:0.1.9 \                   # Image name and tag
  --yaml-config /app/config.yaml \                      # Path to config file inside container
  --env INFERENCE_MODEL=llama32-3b \                     # Model to use (environment-style argument)
  --env VLLM_URL=https://llama32-3b-llama-serve.apps.ocp-beta-test.nerc.mghpcc.org/v1  # URL for VLLM backend



```


### 4. Start the Ollama Model

In a new terminal tab (also inside your virtual env):

```bash
INFERENCE_MODEL=llama3.2:3b llama stack build --template ollama --image-type venv --run
```

This builds and runs the local inference container using the specified model.

---

### 5. Launch the Streamlit UI

In another terminal tab (still in the same `.chenv`):

```bash
streamlit run app.py
```

You’ll see something like:

```
Local URL: http://localhost:8501
```

Open this URL in your browser to interact with ChAI.

---

## 🧠 Architecture Overview

```text
User → Streamlit UI (app.py)
           ↓
      LlamaStack (Ollama)
           ↓
     ┌──────────────┐
     │ ChromaDB API │ ← chroma run --path .chroma_store
     └──────────────┘
```

* **Chat memory** and document context are stored in ChromaDB collections.
* **LLM responses** are generated via LlamaStack → Ollama.
* **Everything runs locally**, but is production-aligned (e.g. OpenShift-ready).

---

## 🛠️ Common Commands

| Command                                   | Purpose                            |
| ----------------------------------------- | ---------------------------------- |
| `chroma run --path .chroma_store`         | Starts ChromaDB HTTP server        |
| `llama stack build --template ollama ...` | Starts Ollama model via LlamaStack |
| `streamlit run app.py`                    | Launches the ChAI frontend         |

---

---

## Logs

```
➜  ChAI git:(main) streamlit run app.py           

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.86.22:8501

2025-05-08 00:45:51 chromadb.telemetry.product.posthog [INFO] Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
2025-05-08 00:45:51 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/auth/identity "HTTP/1.1 200 OK"
2025-05-08 00:45:51 chromadb.telemetry.product.posthog [INFO] Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
2025-05-08 00:45:51 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/tenants/default_tenant "HTTP/1.1 200 OK"
2025-05-08 00:45:51 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database "HTTP/1.1 200 OK"
2025-05-08 00:45:51 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections "HTTP/1.1 200 OK"
2025-05-08 00:45:51 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/6e6c2489-ee91-4b7b-be10-37a4721d6854/get "HTTP/1.1 200 OK"
2025-05-08 00:45:51 ChAIAgent [INFO] ChAIAgent Initialized
2025-05-08 00:45:51 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/tools "HTTP/1.1 200 OK"
2025-05-08 00:45:51 ChAIAgent [INFO] Toolgroup builtin::rag already present
2025-05-08 00:45:51 httpx [INFO] HTTP Request: POST http://localhost:8321/v1/toolgroups "HTTP/1.1 200 OK"
2025-05-08 00:45:51 ChAIAgent [INFO] Registered toolgroup: mcp::chris
2025-05-08 00:45:51 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/tools?toolgroup_id=mcp%3A%3Achris "HTTP/1.1 200 OK"
2025-05-08 00:45:51 ChAIAgent [INFO] Tools available in mcp::chris: ['health_check', 'echo']
2025-05-08 00:45:51 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/vector-dbs "HTTP/1.1 200 OK"
2025-05-08 00:45:51 httpx [INFO] HTTP Request: POST http://localhost:8321/v1/vector-dbs "HTTP/1.1 200 OK"
2025-05-08 00:45:51 ChAIAgent [INFO] Registered vector DB: demo
2025-05-08 00:45:51 ChAIAgent [INFO] Ingesting docs into VectorDB `demo`
2025-05-08 00:46:31 httpx [INFO] HTTP Request: POST http://localhost:8321/v1/tool-runtime/rag-tool/insert "HTTP/1.1 200 OK"
2025-05-08 00:46:31 ChAIAgent [INFO] Inserted 2 documents
2025-05-08 00:46:31 ChAIAgent [INFO] Creating RAG+MCP agent
2025-05-08 00:46:31 httpx [INFO] HTTP Request: POST http://localhost:8321/v1/agents "HTTP/1.1 200 OK"
2025-05-08 00:46:31 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/tools?toolgroup_id=builtin%3A%3Arag%2Fknowledge_search "HTTP/1.1 200 OK"
2025-05-08 00:46:31 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/tools?toolgroup_id=mcp%3A%3Achris "HTTP/1.1 200 OK"
2025-05-08 00:46:31 httpx [INFO] HTTP Request: POST http://localhost:8321/v1/agents/a59b57a6-edc4-48f7-ba20-f241b63ff0b3/session "HTTP/1.1 200 OK"
2025-05-08 00:46:31 chromadb.telemetry.product.posthog [INFO] Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
2025-05-08 00:46:31 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/auth/identity "HTTP/1.1 200 OK"
2025-05-08 00:46:31 chromadb.telemetry.product.posthog [INFO] Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
2025-05-08 00:46:31 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/tenants/default_tenant "HTTP/1.1 200 OK"
2025-05-08 00:46:31 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database "HTTP/1.1 200 OK"
2025-05-08 00:46:31 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections "HTTP/1.1 200 OK"
2025-05-08 00:46:39 ChAIAgent [INFO] ChAIAgent Initialized
2025-05-08 00:46:39 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/tools "HTTP/1.1 200 OK"
2025-05-08 00:46:39 ChAIAgent [INFO] Toolgroup builtin::rag already present
2025-05-08 00:46:39 ChAIAgent [INFO] Toolgroup mcp::chris already present
2025-05-08 00:46:39 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/tools?toolgroup_id=mcp%3A%3Achris "HTTP/1.1 200 OK"
2025-05-08 00:46:39 ChAIAgent [INFO] Tools available in mcp::chris: ['health_check', 'echo']
2025-05-08 00:46:39 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/vector-dbs "HTTP/1.1 200 OK"
2025-05-08 00:46:39 ChAIAgent [INFO] Creating RAG+MCP agent
2025-05-08 00:46:39 httpx [INFO] HTTP Request: POST http://localhost:8321/v1/agents "HTTP/1.1 200 OK"
2025-05-08 00:46:39 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/tools?toolgroup_id=builtin%3A%3Arag%2Fknowledge_search "HTTP/1.1 200 OK"
2025-05-08 00:46:39 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/tools?toolgroup_id=mcp%3A%3Achris "HTTP/1.1 200 OK"
2025-05-08 00:46:39 httpx [INFO] HTTP Request: POST http://localhost:8321/v1/agents/a2a149e7-1b23-4495-b085-45861caf3812/session "HTTP/1.1 200 OK"
2025-05-08 00:46:39 chromadb.telemetry.product.posthog [INFO] Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
2025-05-08 00:46:39 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/auth/identity "HTTP/1.1 200 OK"
2025-05-08 00:46:39 chromadb.telemetry.product.posthog [INFO] Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
2025-05-08 00:46:39 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/tenants/default_tenant "HTTP/1.1 200 OK"
2025-05-08 00:46:39 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database "HTTP/1.1 200 OK"
2025-05-08 00:46:39 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections "HTTP/1.1 200 OK"
2025-05-08 00:46:40 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/pre-flight-checks "HTTP/1.1 200 OK"
2025-05-08 00:46:40 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/6e6c2489-ee91-4b7b-be10-37a4721d6854/add "HTTP/1.1 201 Created"
2025-05-08 00:46:40 chromadb.telemetry.product.posthog [INFO] Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
2025-05-08 00:46:40 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/auth/identity "HTTP/1.1 200 OK"
2025-05-08 00:46:40 chromadb.telemetry.product.posthog [INFO] Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
2025-05-08 00:46:40 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/tenants/default_tenant "HTTP/1.1 200 OK"
2025-05-08 00:46:40 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database "HTTP/1.1 200 OK"
2025-05-08 00:46:40 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections "HTTP/1.1 200 OK"
2025-05-08 00:46:40 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/6e6c2489-ee91-4b7b-be10-37a4721d6854/get "HTTP/1.1 200 OK"
2025-05-08 00:46:40 httpx [INFO] HTTP Request: POST http://localhost:8321/v1/agents/a2a149e7-1b23-4495-b085-45861caf3812/session/351d589e-077a-4179-84ca-1649500803a3/turn "HTTP/1.1 200 OK"

---------- 📍 Step 1: InferenceStep ----------
🛠️ Tool call Generated:
Tool call: knowledge_search, Arguments: {'query': 'ChRIS'}

---------- 📍 Step 2: ToolExecutionStep ----------
🔧 Executing tool...
[
│   TextContentItem(text='knowledge_search tool found 5 chunks:\nBEGIN of knowledge_search tool results.\n', type='text'),
│   TextContentItem(
│   │   text="Result 1:\nDocument_id:overv\nContent: ## ChRIS (ChRIS Research Integration Service) Overview\n\nChRIS is an **opensource distributed software platform** engineered to manage and coordinate computation and data across diverse computing environments. Initially developed for medical image analysis at Boston Children's Hospital, ChRIS has matured into a **general-purpose compute/data platform**. This evolution enables seamless deployment of analyses on a heterogeneous mix of resources, ranging from individual laptops to interconnected workstations, high-performance computing (HPC) clusters, and public cloud infrastructures.\n\nAt its core, ChRIS is designed to handle the execution and data requirements of a specific category of computational applications frequently employed in research settings, particularly within medical image research. These applications are characterized by their **non-interactive nature** once initiated, reliance on **command-line arguments** for runtime specifications, and the collection of all output in **files**.\n\nWhile ChRIS provides a **web-based user interface**, the actual computations are performed by **containerized, Linux-based applications**. These background processes are termed **plugins** within the ChRIS ecosystem, as they seamlessly integrate with the ChRIS backend and are accessible through various frontends.\n\nThe ChRIS architecture consists of a suite of **REST-based web services**, backend web applications, and various client-facing web frontends. The system's primary objective is to **simplify the process for developers to deploy their applications across any computing environment capable of running Linux containers**. By adhering to a standardized command\n",
│   │   type='text'
│   ),
│   TextContentItem(
│   │   text="Result 2:\nDocument_id:overv\nContent: RIS backend and are accessible through various frontends.\n\nThe ChRIS architecture consists of a suite of **REST-based web services**, backend web applications, and various client-facing web frontends. The system's primary objective is to **simplify the process for developers to deploy their applications across any computing environment capable of running Linux containers**. By adhering to a standardized command-line specification for ChRIS applications, the platform facilitates effortless containerization, execution, result collection, data visualization, and collaborative sharing of research software.\n",
│   │   type='text'
│   ),
│   TextContentItem(
│   │   text='Result 3:\nDocument_id:url-0\nContent: 9758,9759,9760,9761,9762,9763,9764,9765,9766,9767,9768,9769,9770,9771,9772,9773,9774,9775,9776,9777,9778,9779,9780,9781,9782,9783,9784,9785,9786,9787,9788,9789,9790,9791,9792,9793,9794,9795,9796,9797,1277,9798,9799,9800,9801,9802,9803,9804,9805,9806,9807,9808,9809,9810,9811,9812,9813,9814,9815,9816,9817,9818,9819,9820,9821,9822,9823,9824,9825],"nodes-scheduler-about","about-default-scheduler","nodes-scheduler-default-about_nodes-scheduler-about","nodes-scheduler-about-use-cases_nodes-scheduler-about","infrastructure-topological-levels_nodes-scheduler-about","affinity_nodes-scheduler-about","anti-affinity_nodes-scheduler-about","nodes-scheduler-profiles","nodes-scheduler-profiles-about_nodes-scheduler-profiles","nodes-scheduler-profiles-configuring_nodes-scheduler-profiles","nodes-scheduler-p\n',
│   │   type='text'
│   ),
│   TextContentItem(
│   │   text='Result 4:\nDocument_id:url-0\nContent: 9884,9885,9886,9887,9888,9889,9890,9891,9892,9893,9894,9895,9896,9897,9898,9899,9900,9901,9902,9903,9904,9905,9906,9907,9908,9909,9910,9911,9912,9913,9914,9915,9916,9917,9918,9919,9920,9921,9922,9923,9924,9925,9926,9927,9928,9929,9930,9931,9932,9933,9934,9935,9936,9937,9938,9939,9940,9941],"nodes-nodes-viewing","nodes-nodes-viewing-listing_nodes-nodes-viewing","nodes-nodes-viewing-listing-pods_nodes-nodes-viewing","nodes-nodes-viewing-memory_nodes-nodes-viewing","nodes-nodes-working","nodes-nodes-working-evacuating_nodes-nodes-working","nodes-nodes-working-updating_nodes-nodes-working","nodes-nodes-working-marking_nodes-nodes-working","deleting-nodes","nodes-nodes-working-deleting_nodes-nodes-working","nodes-nodes-working-deleting-bare-metal_nodes-nodes-working","nodes-nodes-managing","nodes-nodes-managing\n',
│   │   type='text'
│   ),
│   TextContentItem(
│   │   text='Result 5:\nDocument_id:url-0\nContent: 2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025,2026,2027,2028,2029,2030,2031,2032,2033,2034,2035,2036,2037,2038,2039,2040,2041,2042,2043,2044,2045,2046,2047,2048,2049,2050,2051,2052,2053,2054,2055,2056,2057,2058,2059,2060,2061,2062,2063,2064,2065,2066,2067,2068,2069,2070,2071,2072,2073,2074,2075,2076,2077,2078,2079,2080,2081,2082,2083,2084,2085,2086,2087,2088,2089,2090,2091,2092,2093,2094,2095,2096,2097,2098,2099,2100,2101,2102,2103,2104,2105,2106,2107,\n',
│   │   type='text'
│   ),
│   TextContentItem(text='END of knowledge_search tool results.\n', type='text'),
│   TextContentItem(
│   │   text='The above results were retrieved to help answer the user\'s query: "ChRIS". Use them as supporting information only in answering this query.\n',
│   │   type='text'
│   )
]

---------- 📍 Step 3: InferenceStep ----------
🤖 Model Response:
ChRIS (ChRIS Research Integration Service) is an open-source distributed software platform designed for managing and coordinating computation and data across diverse computing environments. It was initially developed for medical image analysis at Boston Children's Hospital but has evolved into a general-purpose compute/data platform, enabling seamless deployment of analyses on various resources, including individual laptops, workstations, HPC clusters, and public cloud infrastructures. ChRIS is designed to handle non-interactive applications with command-line arguments, collecting output in files. The platform consists of REST-based web services, backend web applications, and client-facing web frontends, simplifying the process for developers to deploy their applications across any computing environment capable of running Linux containers.

========== Query processing completed ==========

2025-05-08 00:46:48 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/6e6c2489-ee91-4b7b-be10-37a4721d6854/add "HTTP/1.1 201 Created"
2025-05-08 00:47:05 ChAIAgent [INFO] ChAIAgent Initialized
2025-05-08 00:47:05 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/tools "HTTP/1.1 200 OK"
2025-05-08 00:47:05 ChAIAgent [INFO] Toolgroup builtin::rag already present
2025-05-08 00:47:05 ChAIAgent [INFO] Toolgroup mcp::chris already present
2025-05-08 00:47:05 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/tools?toolgroup_id=mcp%3A%3Achris "HTTP/1.1 200 OK"
2025-05-08 00:47:05 ChAIAgent [INFO] Tools available in mcp::chris: ['health_check', 'echo']
2025-05-08 00:47:05 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/vector-dbs "HTTP/1.1 200 OK"
2025-05-08 00:47:05 ChAIAgent [INFO] Creating RAG+MCP agent
2025-05-08 00:47:05 httpx [INFO] HTTP Request: POST http://localhost:8321/v1/agents "HTTP/1.1 200 OK"
2025-05-08 00:47:05 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/tools?toolgroup_id=builtin%3A%3Arag%2Fknowledge_search "HTTP/1.1 200 OK"
2025-05-08 00:47:05 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/tools?toolgroup_id=mcp%3A%3Achris "HTTP/1.1 200 OK"
2025-05-08 00:47:05 httpx [INFO] HTTP Request: POST http://localhost:8321/v1/agents/51cb27dc-6867-4f67-9fcc-c1bc49e1fe03/session "HTTP/1.1 200 OK"
2025-05-08 00:47:05 chromadb.telemetry.product.posthog [INFO] Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
2025-05-08 00:47:05 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/auth/identity "HTTP/1.1 200 OK"
2025-05-08 00:47:05 chromadb.telemetry.product.posthog [INFO] Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
2025-05-08 00:47:05 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/tenants/default_tenant "HTTP/1.1 200 OK"
2025-05-08 00:47:05 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database "HTTP/1.1 200 OK"
2025-05-08 00:47:05 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections "HTTP/1.1 200 OK"
2025-05-08 00:47:06 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/pre-flight-checks "HTTP/1.1 200 OK"
2025-05-08 00:47:06 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/6e6c2489-ee91-4b7b-be10-37a4721d6854/add "HTTP/1.1 201 Created"
2025-05-08 00:47:06 chromadb.telemetry.product.posthog [INFO] Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
2025-05-08 00:47:06 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/auth/identity "HTTP/1.1 200 OK"
2025-05-08 00:47:06 chromadb.telemetry.product.posthog [INFO] Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
2025-05-08 00:47:06 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/tenants/default_tenant "HTTP/1.1 200 OK"
2025-05-08 00:47:06 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database "HTTP/1.1 200 OK"
2025-05-08 00:47:06 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections "HTTP/1.1 200 OK"
2025-05-08 00:47:06 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/6e6c2489-ee91-4b7b-be10-37a4721d6854/get "HTTP/1.1 200 OK"
2025-05-08 00:47:06 httpx [INFO] HTTP Request: POST http://localhost:8321/v1/agents/51cb27dc-6867-4f67-9fcc-c1bc49e1fe03/session/6d3bdd14-30ad-4ace-858c-d34184c2e071/turn "HTTP/1.1 200 OK"

---------- 📍 Step 1: InferenceStep ----------
🛠️ Tool call Generated:
Tool call: echo, Arguments: {'args': {'text': 'A plugin is a software component that adds new features to an existing application.'}}

---------- 📍 Step 2: ToolExecutionStep ----------
🔧 Executing tool...
{
│   'type': 'text',
│   'text': '{\n  "tool": "echo",\n  "output": {\n    "echoed_args": {\n      "text": "A plugin is a software component that adds new features to an existing application."\n    }\n  },\n  "timestamp": "2025-05-08 04:47:06"\n}',
│   'annotations': None
}

---------- 📍 Step 3: InferenceStep ----------
🛠️ Tool call Generated:
Tool call: knowledge_search, Arguments: {'query': 'ChRIS platform plugin'}

---------- 📍 Step 4: ToolExecutionStep ----------
🔧 Executing tool...
[
│   TextContentItem(text='knowledge_search tool found 5 chunks:\nBEGIN of knowledge_search tool results.\n', type='text'),
│   TextContentItem(
│   │   text="Result 1:\nDocument_id:overv\nContent: RIS backend and are accessible through various frontends.\n\nThe ChRIS architecture consists of a suite of **REST-based web services**, backend web applications, and various client-facing web frontends. The system's primary objective is to **simplify the process for developers to deploy their applications across any computing environment capable of running Linux containers**. By adhering to a standardized command-line specification for ChRIS applications, the platform facilitates effortless containerization, execution, result collection, data visualization, and collaborative sharing of research software.\n",
│   │   type='text'
│   ),
│   TextContentItem(
│   │   text="Result 2:\nDocument_id:overv\nContent: ## ChRIS (ChRIS Research Integration Service) Overview\n\nChRIS is an **opensource distributed software platform** engineered to manage and coordinate computation and data across diverse computing environments. Initially developed for medical image analysis at Boston Children's Hospital, ChRIS has matured into a **general-purpose compute/data platform**. This evolution enables seamless deployment of analyses on a heterogeneous mix of resources, ranging from individual laptops to interconnected workstations, high-performance computing (HPC) clusters, and public cloud infrastructures.\n\nAt its core, ChRIS is designed to handle the execution and data requirements of a specific category of computational applications frequently employed in research settings, particularly within medical image research. These applications are characterized by their **non-interactive nature** once initiated, reliance on **command-line arguments** for runtime specifications, and the collection of all output in **files**.\n\nWhile ChRIS provides a **web-based user interface**, the actual computations are performed by **containerized, Linux-based applications**. These background processes are termed **plugins** within the ChRIS ecosystem, as they seamlessly integrate with the ChRIS backend and are accessible through various frontends.\n\nThe ChRIS architecture consists of a suite of **REST-based web services**, backend web applications, and various client-facing web frontends. The system's primary objective is to **simplify the process for developers to deploy their applications across any computing environment capable of running Linux containers**. By adhering to a standardized command\n",
│   │   type='text'
│   ),
│   TextContentItem(
│   │   text='Result 3:\nDocument_id:url-0\nContent:  level agreements (SLAs) and might not be functionally complete. Red Hat does not recommend using them in production. These features provide early access to upcoming product features, enabling customers to test functionality and provide feedback during the development process.\n\t\t\t\t\t</p><p>\n\t\t\t\t\t\tFor more information about the support scope of Red Hat Technology Preview features, see <a class="link" href="https://access.redhat.com/support/offerings/techpreview/">Technology Preview Features Support Scope</a>.\n\t\t\t\t\t</p></div></rh-alert><section class="section" id="enabling-kdump"><div class="titlepage"><div><div><h4 class="title">7.4.1.1.\xa0Enabling kdump</h4></div></div></div><p>\n\t\t\t\t\t\tRHCOS ships with the <code class="literal">kexec-tools</code> package, but manual configuration is required to enable the <code class="literal">kdump</code> service.\n\t\t\t\t\t</p><div class="formalpara"><p class="title"><strong>Procedure</strong></p><p>\n\t\t\t\t\t\t\tPerform the following steps to enable kdump on RHCOS.\n\t\t\t\t\t\t</p></div><div class="orderedlist"><ol class="orderedlist" type="1"><li class="listitem"><p class="simpara">\n\t\t\t\t\t\t\t\tTo reserve memory for the crash kernel during the first kernel booting, provide\n',
│   │   type='text'
│   ),
│   TextContentItem(
│   │   text='Result 4:\nDocument_id:url-0\nContent: cda><a href="https://www.redhat.com/architect/portfolio/" data-analytics-category="All Red Hat|Learning resources" data-analytics-text="Architecture center" data-v-711a4cda>Architecture center</a></li></ul></li><li data-v-711a4cda><span data-v-711a4cda>Open source communities</span><ul data-v-711a4cda><li data-v-711a4cda><a href="https://access.redhat.com/accelerators" data-analytics-category="All Red Hat|Open source communities" data-analytics-text="Global advocacy" data-v-711a4cda>Global advocacy</a></li><li data-v-711a4cda><a href="https://www.redhat.com/en/about/our-community-contributions" data-analytics-category="All Red Hat|Open source communities" data-analytics-text="How we contribute" data-v-711a4cda>How we contribute</a></li></ul></li></ul></div></li></ul></div></nav></header><header class="pfe-navigation-content-page-container" data-v-711a4cda><pfe-navigation id="pfe-navigation" full-width pf-sticky="true" lang="en" data-v-711a4cda><nav class="pfe-navigation" aria-label="Main Navigation" data-v-711a4c\n',
│   │   type='text'
│   ),
│   TextContentItem(
│   │   text='Result 5:\nDocument_id:url-0\nContent:  class="hidden-at-desktop hidden-at-tablet buttons" data-v-711a4cda><a href="https://www.redhat.com/en/summit" data-analytics-category="More Red Hat" data-analytics-text="Summit" data-v-711a4cda><img src="/_nuxt/Red-Hat-Summit-logo.DsUYtlmu.svg" width="48" height="25" alt="Red Hat Summit" data-v-711a4cda> Red\xa0Hat Summit</a><a href="https://access.redhat.com/" data-analytics-category="More Red Hat" data-analytics-text="Support" data-v-711a4cda>Support</a><a href="https://console.redhat.com/" data-analytics-category="More Red Hat" data-analytics-text="Console" data-v-711a4cda>Console</a><a href="https://developers.redhat.com/" data-analytics-category="More Red Hat" data-analytics-text="Developers" data-v-711a4cda>Developers</a><a href="https://www.redhat.com/en/products/trials" data-analytics-category="More Red Hat" data-analytics-text="Start a trial" data-v-711a4cda>Start a trial</a><a href="https://www.redhat.com/en/contact" data-analytics-category="More Red Hat" data-analytics-text="Contact" data-v-711a4c\n',
│   │   type='text'
│   ),
│   TextContentItem(text='END of knowledge_search tool results.\n', type='text'),
│   TextContentItem(
│   │   text='The above results were retrieved to help answer the user\'s query: "ChRIS platform plugin". Use them as supporting information only in answering this query.\n',
│   │   type='text'
│   )
]

---------- 📍 Step 5: InferenceStep ----------
🤖 Model Response:
A plugin is a software component that adds new features to an existing application.

========== Query processing completed ==========

2025-05-08 00:47:19 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/6e6c2489-ee91-4b7b-be10-37a4721d6854/add "HTTP/1.1 201 Created"
2025-05-08 00:47:54 ChAIAgent [INFO] ChAIAgent Initialized
2025-05-08 00:47:54 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/tools "HTTP/1.1 200 OK"
2025-05-08 00:47:54 ChAIAgent [INFO] Toolgroup builtin::rag already present
2025-05-08 00:47:54 ChAIAgent [INFO] Toolgroup mcp::chris already present
2025-05-08 00:47:54 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/tools?toolgroup_id=mcp%3A%3Achris "HTTP/1.1 200 OK"
2025-05-08 00:47:54 ChAIAgent [INFO] Tools available in mcp::chris: ['health_check', 'echo']
2025-05-08 00:47:54 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/vector-dbs "HTTP/1.1 200 OK"
2025-05-08 00:47:54 ChAIAgent [INFO] Creating RAG+MCP agent
2025-05-08 00:47:54 httpx [INFO] HTTP Request: POST http://localhost:8321/v1/agents "HTTP/1.1 200 OK"
2025-05-08 00:47:54 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/tools?toolgroup_id=builtin%3A%3Arag%2Fknowledge_search "HTTP/1.1 200 OK"
2025-05-08 00:47:54 httpx [INFO] HTTP Request: GET http://localhost:8321/v1/tools?toolgroup_id=mcp%3A%3Achris "HTTP/1.1 200 OK"
2025-05-08 00:47:54 httpx [INFO] HTTP Request: POST http://localhost:8321/v1/agents/dfea885b-1369-4fae-848c-882b02ecf95e/session "HTTP/1.1 200 OK"
2025-05-08 00:47:54 chromadb.telemetry.product.posthog [INFO] Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
2025-05-08 00:47:54 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/auth/identity "HTTP/1.1 200 OK"
2025-05-08 00:47:54 chromadb.telemetry.product.posthog [INFO] Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
2025-05-08 00:47:54 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/tenants/default_tenant "HTTP/1.1 200 OK"
2025-05-08 00:47:54 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database "HTTP/1.1 200 OK"
2025-05-08 00:47:54 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections "HTTP/1.1 200 OK"
2025-05-08 00:47:55 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/pre-flight-checks "HTTP/1.1 200 OK"
2025-05-08 00:47:55 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/6e6c2489-ee91-4b7b-be10-37a4721d6854/add "HTTP/1.1 201 Created"
2025-05-08 00:47:55 chromadb.telemetry.product.posthog [INFO] Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
2025-05-08 00:47:55 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/auth/identity "HTTP/1.1 200 OK"
2025-05-08 00:47:55 chromadb.telemetry.product.posthog [INFO] Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
2025-05-08 00:47:55 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/tenants/default_tenant "HTTP/1.1 200 OK"
2025-05-08 00:47:55 httpx [INFO] HTTP Request: GET http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database "HTTP/1.1 200 OK"
2025-05-08 00:47:55 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections "HTTP/1.1 200 OK"
2025-05-08 00:47:55 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/6e6c2489-ee91-4b7b-be10-37a4721d6854/get "HTTP/1.1 200 OK"
2025-05-08 00:47:55 httpx [INFO] HTTP Request: POST http://localhost:8321/v1/agents/dfea885b-1369-4fae-848c-882b02ecf95e/session/77ae5671-9f70-4f2f-81d5-499a831d2997/turn "HTTP/1.1 200 OK"

---------- 📍 Step 1: InferenceStep ----------
🛠️ Tool call Generated:
Tool call: health_check, Arguments: {'args': {}}

---------- 📍 Step 2: ToolExecutionStep ----------
🔧 Executing tool...
{
│   'type': 'text',
│   'text': '{\n  "tool": "health_check",\n  "output": {\n    "status": "\\u2705 up",\n    "message": "MCP server is alive"\n  },\n  "timestamp": "2025-05-08 04:47:56"\n}',
│   'annotations': None
}

---------- 📍 Step 3: InferenceStep ----------
🤖 Model Response:
The ChRIS MCP server is currently healthy and online.

========== Query processing completed ==========

2025-05-08 00:47:57 httpx [INFO] HTTP Request: POST http://localhost:8000/api/v2/tenants/default_tenant/databases/default_database/collections/6e6c2489-ee91-4b7b-be10-37a4721d6854/add "HTTP/1.1 201 Created"


```

---

## 🩺 Troubleshooting

### Chroma Errors

* **Error:** `PersistentClient not supported`

  * **Fix:** Make sure you're running `chroma run --path .chroma_store` and using `HttpClient` in code

* **Error:** `localhost:8000 refused connection`

  * **Fix:** Ensure the Chroma server is running before launching the app

---

## 📁 File/Folder Structure

```
ChAI/
├── app.py                  # Streamlit UI
├── memory/
│   └── chroma_store.py     # ChromaMemoryStore using HttpClient
├── agents/
│   └── chai.py             # ChAI agent logic
├── .chroma_store/          # Auto-created persistent vector store
├── requirements.txt
└── README.md
```

---

## 📌 Notes

* The `.chroma_store/` folder is your persistent vector DB — similar to a PVC in production.
* You can use the same architecture on OpenShift by deploying the Chroma server and mounting this folder via a PVC.

---

## 🚀 Future Enhancements

* Add OpenShift `Deployment + PVC` YAMLs
* Dockerize ChromaDB
* Integrate RAG document upload in UI
* Add `analyze` mode for input summarization

---

## 🧩 Credits

Built using:

* [ChromaDB](https://github.com/chroma-core/chroma)
* [Ollama](https://ollama.com)
* [LlamaStack](https://llama-stack.readthedocs.io/en/latest)
* [Streamlit](https://streamlit.io)

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE). You are free to use, modify, and distribute this software with proper attribution.

