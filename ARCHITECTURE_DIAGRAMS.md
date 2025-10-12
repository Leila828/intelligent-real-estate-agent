# System Architecture Diagrams

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        UI[Web Browser]
        Mobile[Mobile Browser]
        API[API Clients]
    end
    
    subgraph "Application Layer"
        Flask[Flask Application Server]
        Router[Route Handler]
        NLP[Natural Language Processor]
        Cache[Cache Manager]
        Auth[Authentication Layer]
    end
    
    subgraph "Business Logic Layer"
        Search[Search Engine]
        Question[Question Handler]
        Price[Price Estimator]
        Map[Map Service]
    end
    
    subgraph "Data Layer"
        SQLite[(SQLite Database)]
        CacheDB[(Cache Storage)]
        Files[File Storage]
    end
    
    subgraph "External Services"
        PF[Property Finder API]
        Ollama[Ollama LLM Service]
        Maps[Map Services]
        Images[Image CDN]
    end
    
    UI --> Flask
    Mobile --> Flask
    API --> Flask
    
    Flask --> Router
    Router --> NLP
    Router --> Cache
    Router --> Auth
    
    NLP --> Search
    NLP --> Question
    NLP --> Price
    
    Search --> SQLite
    Question --> SQLite
    Price --> SQLite
    
    Cache --> CacheDB
    Search --> PF
    Question --> Ollama
    Map --> Maps
    Flask --> Images
```

## 2. Data Flow Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant F as Flask App
    participant N as NLP Parser
    participant O as Ollama LLM
    participant P as Property Finder
    participant C as Cache Layer
    participant D as Database
    participant R as Response Generator

    U->>F: Natural Language Query
    F->>N: Parse Query
    N->>O: AI Processing (if needed)
    O-->>N: Structured Output
    N-->>F: Parsed Parameters
    
    F->>C: Check Cache
    alt Cache Hit
        C-->>F: Cached Results
    else Cache Miss
        F->>P: API Request
        P-->>F: Property Data
        F->>D: Store in Database
        F->>C: Update Cache
    end
    
    F->>R: Format Response
    R-->>F: JSON Response
    F-->>U: Property Listings
```

## 3. Caching Strategy Architecture

```mermaid
graph TD
    A[User Query] --> B{Query Parser}
    B --> C[Generate Cache Key]
    C --> D{Cache Lookup}
    
    D -->|Hit| E[Return Cached Data]
    D -->|Miss| F[External API Call]
    
    F --> G[Data Transformation]
    G --> H[Store in Cache]
    H --> I[Return Fresh Data]
    
    J[Cache Expiry] --> K[Cleanup Expired Entries]
    K --> L[Update Cache Statistics]
    
    M[Cache Monitoring] --> N[Performance Metrics]
    N --> O[Optimization Recommendations]
```

## 4. API Integration Architecture

```mermaid
graph LR
    subgraph "Internal Services"
        A[Flask App]
        B[Database]
        C[Cache Layer]
    end
    
    subgraph "External APIs"
        D[Property Finder API]
        E[Ollama LLM]
        F[Map Services]
        G[Image CDN]
    end
    
    A --> D
    A --> E
    A --> F
    A --> G
    
    A --> B
    A --> C
    
    D --> H[Property Data]
    E --> I[AI Responses]
    F --> J[Map Data]
    G --> K[Images]
    
    H --> A
    I --> A
    J --> A
    K --> A
```

## 5. Database Schema Relationships

```mermaid
erDiagram
    SEARCH_QUERIES {
        int query_id PK
        string query_string UK
        timestamp created_at
        timestamp expires_at
    }
    
    CACHED_PROPERTIES {
        string id PK
        int query_id FK
        string title
        float price
        float area
        int rooms
        int baths
        string purpose
        string completion_status
        float latitude
        float longitude
        string location_name
        string cover_photo_url
        string all_image_urls
        string agency_name
        string contact_name
        string mobile_number
        string whatsapp_number
        float down_payment_percentage
    }
    
    SEARCH_QUERIES ||--o{ CACHED_PROPERTIES : "has many"
```

## 6. User Journey Flow

```mermaid
journey
    title User Property Search Journey
    section Discovery
      Visit Website: 5: User
      Enter Search Query: 4: User
      Submit Search: 5: User
    section Search Processing
      NLP Processing: 3: System
      Cache Check: 4: System
      API Call (if needed): 2: System
      Data Processing: 3: System
    section Results
      View Property List: 5: User
      Click Property Details: 4: User
      View Property Images: 5: User
      Check Map Location: 4: User
      Contact Agent: 5: User
```

## 7. Error Handling Architecture

```mermaid
graph TD
    A[Request] --> B{Validation}
    B -->|Valid| C[Process Request]
    B -->|Invalid| D[Return 400 Error]
    
    C --> E{API Call}
    E -->|Success| F[Process Response]
    E -->|Timeout| G[Return 408 Error]
    E -->|API Error| H[Return 502 Error]
    
    F --> I{Data Processing}
    I -->|Success| J[Return Results]
    I -->|Error| K[Return 500 Error]
    
    L[Logging System] --> M[Error Tracking]
    M --> N[Performance Monitoring]
    N --> O[Alert System]
```

## 8. Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        Dev[Local Development]
        Test[Testing Environment]
    end
    
    subgraph "Production Environment"
        LB[Load Balancer]
        App1[App Instance 1]
        App2[App Instance 2]
        App3[App Instance 3]
    end
    
    subgraph "Database Layer"
        Primary[(Primary Database)]
        Replica[(Read Replica)]
    end
    
    subgraph "External Services"
        CDN[Content Delivery Network]
        API[External APIs]
        Storage[File Storage]
    end
    
    Dev --> Test
    Test --> LB
    LB --> App1
    LB --> App2
    LB --> App3
    
    App1 --> Primary
    App2 --> Primary
    App3 --> Primary
    
    App1 --> Replica
    App2 --> Replica
    App3 --> Replica
    
    App1 --> CDN
    App2 --> CDN
    App3 --> CDN
    
    App1 --> API
    App2 --> API
    App3 --> API
```

## 9. Security Architecture

```mermaid
graph TD
    A[Client Request] --> B[Rate Limiting]
    B --> C[Input Validation]
    C --> D[Authentication]
    D --> E[Authorization]
    E --> F[Request Processing]
    
    G[Security Headers] --> H[CORS Configuration]
    H --> I[CSRF Protection]
    I --> J[XSS Prevention]
    
    K[Data Encryption] --> L[API Key Management]
    L --> M[Secure Communication]
    M --> N[Audit Logging]
```

## 10. Performance Monitoring Architecture

```mermaid
graph LR
    subgraph "Application Metrics"
        A[Response Time]
        B[Throughput]
        C[Error Rate]
        D[Cache Hit Rate]
    end
    
    subgraph "System Metrics"
        E[CPU Usage]
        F[Memory Usage]
        G[Disk I/O]
        H[Network I/O]
    end
    
    subgraph "Business Metrics"
        I[User Queries]
        J[Property Views]
        K[API Calls]
        L[Cache Performance]
    end
    
    A --> M[Monitoring Dashboard]
    B --> M
    C --> M
    D --> M
    E --> M
    F --> M
    G --> M
    H --> M
    I --> M
    J --> M
    K --> M
    L --> M
    
    M --> N[Alerting System]
    N --> O[Performance Optimization]
```
