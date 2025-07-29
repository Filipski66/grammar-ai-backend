from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/solve", methods=["POST"])
def solve():
    data = request.get_json()
    question = data.get("question", "")
    choices = data.get("choices", [])

    if not question:
        return jsonify({"error": "No question provided"}), 400

    if choices:
        joined = "\\n".join([f"{chr(65+i)}. {c}" for i, c in enumerate(choices)])
        prompt = f"Spørgsmål: {question}\\n{joined}\\n\\nSvar med den bedste mulighed (f.eks. A, B, C):"
    else:
        prompt = f"Besvar dette grammatisk korrekt:\\n{question}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du er en grammatikhjælper."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=30
        )
        answer = response.choices[0].message.content.strip()

        if choices:
            for i, choice in enumerate(choices):
                if answer.upper().startswith(chr(65+i)) or choice.lower() in answer.lower():
                    return jsonify({"correct": choice})
            return jsonify({"correct": choices[0]})
        else:
            return jsonify({"correct": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
