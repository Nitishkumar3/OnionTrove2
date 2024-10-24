import re
import os

def TextToString(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()

def OnionExtractor(content):
    onion_pattern = re.compile(
        r'(?:https?://)?([a-z2-7]{16,56}\.onion)(?:/\S*)?',
        re.IGNORECASE
    )
    try:

        matches = onion_pattern.findall(content)
        unique_domains = sorted(list(set(matches)))
        filename = os.path.basename(file_path)      
        if unique_domains:
 
            return unique_domains
        else:
            return []
        
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return set()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return set()
    
file_path = r"data.json" 
Text = TextToString(file_path)
OnionLinks = OnionExtractor(Text)
print(OnionLinks)


# import logging
# from flask import Flask, request, render_template_string, flash, redirect, url_for
# import chardet
# from logging.handlers import RotatingFileHandler

# app = Flask(__name__)
# app.secret_key = 'supersecretkey'  # Required for flash messages

# # Configure logging
# handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=5)
# handler.setLevel(logging.ERROR)
# app.logger.addHandler(handler)

# # Basic HTML template for uploading a file
# HTML_TEMPLATE = """
# <!doctype html>
# <html lang="en">
#   <head>
#     <title>File Upload</title>
#   </head>
#   <body>
#     <h1>Upload a File</h1>
#     <form method="POST" enctype="multipart/form-data">
#       <input type="file" name="file">
#       <input type="submit" value="Upload">
#     </form>
#     <h2>Messages:</h2>
#     {% with messages = get_flashed_messages() %}
#       {% if messages %}
#         <ul>
#           {% for message in messages %}
#             <li>{{ message }}</li>
#           {% endfor %}
#         </ul>
#       {% endif %}
#     {% endwith %}
#     <h2>File Content:</h2>
#     <pre>{{ file_content }}</pre>
#   </body>
# </html>
# """

# @app.route("/", methods=["GET", "POST"])
# def upload_file():
#     file_content = ""

#     if request.method == "POST":
#         try:
#             uploaded_file = request.files.get("file")
#             if uploaded_file:
#                 # Read file in binary mode
#                 file_data = uploaded_file.read()

#                 # Detect the encoding of the file using chardet
#                 result = chardet.detect(file_data)
#                 encoding = result['encoding'] if result['encoding'] else 'utf-8'

#                 try:
#                     # Decode the file content using detected encoding
#                     file_content = file_data.decode(encoding)
#                     flash("File uploaded successfully", "success")
#                 except Exception as decode_err:
#                     flash("Error decoding file content", "error")
#                     app.logger.error(f"Error decoding file: {decode_err}")

#         except Exception as e:
#             flash("An error occurred during file upload", "error")
#             app.logger.error(f"An error occurred: {e}")

#         return render_template_string(HTML_TEMPLATE, file_content=file_content)

#     # Render the template on GET requests
#     return render_template_string(HTML_TEMPLATE, file_content=file_content)

# if __name__ == "__main__":
#     app.run(debug=True)
