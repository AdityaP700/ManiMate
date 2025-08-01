flowchart TD
  %% Modern Styling
  classDef api fill:#667eea,stroke:#764ba2,stroke-width:3px,color:#fff
  classDef process fill:#f093fb,stroke:#f5576c,stroke-width:2px,color:#fff
  classDef decision fill:#4facfe,stroke:#00f2fe,stroke-width:3px,color:#fff
  classDef storage fill:#43e97b,stroke:#38f9d7,stroke-width:2px,color:#fff
  classDef render fill:#fa709a,stroke:#fee140,stroke-width:2px,color:#fff
  classDef error fill:#ff6b6b,stroke:#ee5a24,stroke-width:2px,color:#fff

  %% Main Flow
  A[🚀 POST /api/render]:::api 
  A --> B[⚡ FastAPI + Uvicorn]:::process
  B --> C[✅ Pydantic Validation]:::process
  C --> D[🧠 Generate Manim Code]:::process
  
  %% AI Decision Point
  D --> E{🤖 OpenAI API}:::decision
  E -->|✓| F[📝 Extract Python Code]:::process
  E -->|✗| G[🔄 Fallback to Gemini]:::process
  G --> F
  
  %% Queue & Processing
  F --> H[📋 Celery Queue]:::storage
  H --> I[⚙️ Worker Process]:::render
  I --> J[📁 Setup Environment]:::render
  J --> K[🎬 Manim Render]:::render
  K --> L[☁️ Upload to GCS]:::storage
  L --> M[🎯 Return URL]:::api

  %% Error Handling (Condensed)
  subgraph "🚨 Error Handling"
    direction TB
    E1[Validation Error]:::error
    E2[API Failure]:::error  
    E3[Render Error]:::error
    E4[Upload Error]:::error
  end
  
  %% Error Connections
  C -.-> E1
  E -.-> E2
  K -.-> E3
  L -.-> E4

  %% Styling
  style A fill:#667eea,stroke:#764ba2,stroke-width:4px
  style M fill:#43e97b,stroke:#38f9d7,stroke-width:4px