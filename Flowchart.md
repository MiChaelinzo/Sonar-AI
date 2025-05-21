```mermaid
flowchart TD
    A[Sonar Data Sources]
    A1[Sea Sonar]
    A2[Land Sonar]
    A3[Air Sonar]
    A --> A1
    A --> A2
    A --> A3

    B[Data Ingestion Layer]
    A1 --> B
    A2 --> B
    A3 --> B

    C[Preprocessing & Cleaning]
    B --> C

    D1[Signal Processing]
    D2[Noise Reduction]
    C --> D1
    C --> D2

    E[Data Fusion & Alignment]
    D1 --> E
    D2 --> E

    F[Visualization Engine (Streamlit)]
    E --> F

    G1[Advanced Sonar Visualization]
    G2[Interactive Charts & Maps]
    G3[Anomaly & Pattern Detection]
    F --> G1
    F --> G2
    F --> G3

    H[Perplexity AI Assistant (Sonar Perplexity AI)]
    G1 --> H
    G2 --> H
    G3 --> H

    I[User Interface]
    H --> I
    F --> I

    J[Users (Researchers, Operators, Public)]
    I --> J
```
