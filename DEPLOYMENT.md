# Deployment Guide for RAG API on Render

## Prerequisites
- GitHub account
- Render account (free tier available)
- Your API keys ready

## Files for Deployment
- ✅ Procfile - Tells Render how to run your app
- ✅ runtime.txt - Specifies Python version
- ✅ requirements.txt - Lists dependencies
- ✅ All your modular Python files

## Environment Variables Needed on Render
Set these in Render dashboard:
- GOOGLE_API_KEY
- OPENAI_API_KEY  
- PINECONE_API_KEY
- API_KEY

## Deployment Steps
1. Push code to GitHub
2. Connect GitHub repo to Render
3. Configure environment variables
4. Deploy!

## Testing
Your API will be available at: https://your-app-name.onrender.com
