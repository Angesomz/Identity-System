# INSA Identity System - Distributed Biometric Identity Platform

## 🚀 System Overview
A million-scale, high-precision national identity verification platform designed for enterprise-grade security and scalability. This system uses a distributed architecture with microservices for liveness detection, face processing, embedding generation, and vector matching.

## 🏗 Architecture
- **Gateway**: Secure API entry point with mTLS and Rate Limiting.
- **Services**:
  - `Liveness`: Anti-spoofing checks.
  - `Face Processing`: RetinaFace detection and alignment.
  - `Embedding`: ArcFace vector generation.
  - `Matching`: FAISS IVF+HNSW vector search.
  - `Identity Resolver`: Final identity verification and national ID adapter.
- **Data**:
  - PostgreSQL: Metadata and relational data.
  - Redis: Caching and rate limiting.
  - Vector Cluster: Distributed FAISS indices.

## 🛠 Tech Stack
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **ML/AI**: RetinaFace, ArcFace, PyTorch
- **Vector Search**: FAISS (GPU enabled where available)
- **Database**: PostgreSQL, Redis
- **Infra**: Docker, Kubernetes

## 📦 Setup & Deployment
Refer to `deployment/README.md` for detailed instructions.

### Quick Start (Local)
```bash
cd insa_identity_system
pip install -r requirements.txt
python -m gateway.main
```

## 🔒 Security
- Zero-Trust Architecture
- mTLS between internal services
- AES-256 Encryption for embeddings at rest
- Full Audit Logging

## 📊 Monitoring
Prometheus metrics available at `/metrics`.
