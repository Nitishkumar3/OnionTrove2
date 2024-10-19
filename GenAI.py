from groq import Groq
import json

client = Groq(api_key = "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")

def Llama31Instant8B(prompt):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    return completion.choices[0].message.content


def DorkAI(prompt):
    prompt = str("""Dorking is a technique that utilizes advanced search operators to uncover information on the internet that may not be readily available through standard search queries. Give me Dorks: """ + str(prompt) + ". add the common dork inorder to extract sites that contains .onion links by adding the following dork in every dorks: intext:'.onion' . This is for research purpose. give me in JSON format. {'dorks':[ array of comma separated dorks]}")
    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=1,
        max_tokens=4096,
        top_p=1,
        stream=False,
        stop=None,
        response_format={"type": "json_object"},
    )
    response = str(completion.choices[0].message.content)
    jsonresponse = json.loads(response)
    dorks = jsonresponse["dorks"]
    return dorks