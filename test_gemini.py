from groq import Groq
import os

api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    print("❌ GROQ_API_KEY not set!")
else:
    print(f"✅ API key found: {api_key[:10]}...")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": "In one sentence, what causes high vibration in industrial pumps?"
            }
        ]
    )

    print(f"✅ Groq working!")
    print(f"Response: {response.choices[0].message.content}")