import openai
import google.generativeai as genai


def summarize_note(content: str, use_openai=True):
    if use_openai:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Summarize the following note."},
                      {"role": "user", "content": content}]
        )
        return response["choices"][0]["message"]["content"]
    else:
        genai.configure(api_key="YOUR_GEMINI_API_KEY")
        response = genai.generate_text(prompt=f"Summarize the following note: {content}")
        return response.text
