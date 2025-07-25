# 🗣️ Voice Agent for Christian Tee Shop (Dify + LiveKit + Python)

## Overview

This is a custom voice agent built using **LiveKit**, **Dify**, and **Python** to assist with operations in a Christian t-shirt e-commerce shop. The agent handles spoken input, connects to an LLM for intelligent responses, retrieves order data, and pulls from a knowledge base of shop specific questions

## Features

- 🎧 **Real-time voice interaction** via LiveKit audio streams using WebRTC tech
- 🧠 **LLM-powered responses** using Dify’s language model API
- 📦 **Order data retrieval**: Agent can fetch order details when provided an order number (via internal API)
- 📚 **Knowledge base integration**: Pulls from a knowledge base to answer shop specfic questions
- 🔒 **Context-aware and secure**: LLM access is scoped and limited to business-specific data

## Tech Stack

- **Voice SDK:** LiveKit Audio (WebRTC)
- **LLM Interface:** Dify
- **Backend:** Python (Flask)
- **Data Sources:** API request to MongoDB database
- **Knowledge Base:** Vector store or Dify’s inbuilt knowledge space

### 🗣️ Chatbot UI – Voice Mode

![Chatbot Voice UI](https://i.postimg.cc/zy4ZjfMB/78-B14-BC3-88-A9-4-AF0-8-C80-5-B762-FC055-F7-L0-001-30-03-2025-6-09-26-PM.jpg)

---

### 💬 Chatbot UI – Text Mode

![Chatbot Text UI](https://i.postimg.cc/t1P0mjQz/DDADB5-D1-5-A3-D-4396-B5-E0-4-B8-ADFCD27-CC-L0-001-30-03-2025-6-18-29-PM.jpg)

---

### 🧠 Chatbot Logic – Dify Flow (Part 1)

![Dify Flow Part 1](https://i.postimg.cc/QVqD3hB4/Screenshot-2025-03-30-at-6-24-52-PM.png)

---

### 🧠 Chatbot Logic – Dify Flow (Part 2)

![Dify Flow Part 2](https://i.postimg.cc/SnnbC9g3/Screenshot-2025-03-30-at-6-52-51-PM.png)
