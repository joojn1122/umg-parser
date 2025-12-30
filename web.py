from flask import Flask, render_template, request
from convert import convert
from constants import Message, INDENT
import sys

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert_endpoint():
    js = request.get_json()

    umg_text = js.get("umg_text", "")
    use_translated = js.get("use_translated", False)

    if not umg_text or not isinstance(umg_text, str):
        return {"error": "Invalid UMG text"}, 400

    try:
        Message.Translate = use_translated
        name, verse_code, widgets = convert(umg_text, 0)

        added_content = ""

        if use_translated:
            messages_content = ""

            for widget in widgets:
                if hasattr(widget, "text"):
                    text = getattr(widget, "text")

                    if isinstance(text, Message) and text.translation_key and text.include_in_translation_file:
                        check_key = f"{text.translation_key}<public><localizes>"
                        
                        # Check if the message already exists in the file
                        if check_key in messages_content:
                            continue
                        
                        # Needs to manually add types for arguments
                        args_str = ", ".join([f"{arg}: " for arg in text.params])
                        if args_str:
                            args_str = f"({args_str})"

                        # Add the message to the file
                        messages_content += f"\n{INDENT}{text.translation_key}<public><localizes>{args_str}: message = \"{text.message}\""

            if messages_content:
                added_content = "Messages<public> := module:" + messages_content + "\n\n\n"

        return {"verse_code": added_content + verse_code}

    except ValueError as e:
        return {"error": e.args[0]}, 400

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=3001,
        debug=len(sys.argv) > 1 and sys.argv[1] == "debug"
    )
