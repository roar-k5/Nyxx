# NYXX API Documentation

Base URL:

```text
http://localhost:8000
```

## Health Check

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

## Config Status

```http
GET /config/status
```

Response:

```json
{
  "groqConfigured": true,
  "mongoConfigured": true,
  "model": "llama-3.3-70b-versatile"
}
```

This endpoint is safe for development checks. It does not return secret values.

## Send Chat Message

```http
POST /api/chat/send
Content-Type: application/json
```

Request body:

```json
{
  "message": "I feel anxious today",
  "history": [
    {
      "role": "user",
      "content": "Hi"
    },
    {
      "role": "assistant",
      "content": "What's up?"
    }
  ]
}
```

Fields:

- `message`: required user message
- `history`: optional array of previous messages
- `history.role`: `user`, `assistant`, or `system`
- `history.content`: message text

The backend uses only the last five history messages in the prompt.

Response:

```json
{
  "response": "That sounds heavy. Want to tell me what triggered it?",
  "emotion": "anxious",
  "crisis": false
}
```

## Internal Processing

The chat endpoint performs these steps:

```text
1. Validate request body
2. Analyze user message with Groq
3. Evaluate safety risk
4. Build NYXX persona prompt
5. Generate assistant response with Groq
6. Filter or annotate unsafe/elevated-risk responses
7. Save user and assistant messages to MongoDB when available
8. Return JSON to frontend
```

## Error Behavior

If `GROQ_API_KEY` is missing:

```json
{
  "response": "NYXX is not configured yet. Add GROQ_API_KEY to the backend environment, then try again.",
  "emotion": "neutral",
  "crisis": false
}
```

If response generation fails:

```json
{
  "response": "I am having trouble connecting right now, but I am still here. Try again in a moment.",
  "emotion": "neutral",
  "crisis": false
}
```

## Safety Notes

For crisis messages, the response should:

- Drop casual tone
- Focus on immediate safety
- Encourage real-world help
- Avoid jokes and emojis
- Never provide methods or instructions for self-harm

For off-topic or medicine requests, the response should:

- Avoid giving the requested information
- Be honest about limitations
- Steer back to mental health support
