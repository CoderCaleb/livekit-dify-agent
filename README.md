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
- **Backend:** Python (FastAPI or Flask)
- **Data Sources:** REST APIs + internal order DB
- **Knowledge Base:** Vector store or Dify’s inbuilt knowledge space

