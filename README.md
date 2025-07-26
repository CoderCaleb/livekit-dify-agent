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

<h3>🗣️ Chatbot UI – Voice Mode</h3>
<img src="https://ik.imagekit.io/uuuwbrc6wu/78B14BC3-88A9-4AF0-8C80-5B762FC055F7_L0_001-30_03_2025,%206_09_26%20PM.jpg?updatedAt=1753421649670" alt="Chatbot Voice UI" width="700"/>

<hr/>

<h3>💬 Chatbot UI – Text Mode</h3>
<img src="https://ik.imagekit.io/uuuwbrc6wu/DDADB5D1-5A3D-4396-B5E0-4B8ADFCD27CC_L0_001-30_03_2025,%206_18_29%20PM.jpg?updatedAt=1753421649694" alt="Chatbot Text UI" width="700"/>

<hr/>

<h3>🧠 Chatbot Logic – Dify Flow (Part 1)</h3>
<img src="https://ik.imagekit.io/uuuwbrc6wu/Screenshot%202025-03-30%20at%206.24.52%20PM.png?updatedAt=1753421649375" alt="Dify Flow Part 1" width="700"/>

<hr/>

<h3>🧠 Chatbot Logic – Dify Flow (Part 2)</h3>
<img src="https://ik.imagekit.io/uuuwbrc6wu/Screenshot%202025-03-30%20at%206.52.51%20PM.png?updatedAt=1753421649543" alt="Dify Flow Part 2" width="700"/>
