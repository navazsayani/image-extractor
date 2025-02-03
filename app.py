import os
from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from modules.info_extractor import AIInfoExtractor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for required API key
if not os.getenv('OPENROUTER_API_KEY'):
    raise ValueError("OPENROUTER_API_KEY environment variable is required")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tiff', 'bmp'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        try:
            # Save the uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Process the image using AI
                info_extractor = AIInfoExtractor()
                extracted_info = info_extractor.extract_info(filepath)
                
                # Clean up the uploaded file
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                # Check if we got any results
                if not extracted_info:
                    flash('Could not extract any information from the document. Please ensure it is a clear image with readable text.')
                    return redirect(url_for('index'))
                
                return render_template('results.html', results=extracted_info)
                
            except Exception as e:
                # Clean up the uploaded file in case of processing error
                if os.path.exists(filepath):
                    os.remove(filepath)
                error_msg = str(e)
                print(f"Processing error: {error_msg}")
                if "timeout" in error_msg.lower():
                    flash('Request timed out. Please try with a smaller image or try again later.')
                elif "file is too large" in error_msg.lower():
                    flash('Image file is too large. Maximum size is 15MB.')
                elif "invalid or corrupted" in error_msg.lower():
                    flash('The image file appears to be corrupted or in an unsupported format.')
                elif "file not found" in error_msg.lower():
                    flash('The uploaded file could not be found. Please try uploading again.')
                else:
                    flash(f'Error processing document: {error_msg}')
                return redirect(url_for('index'))
                
        except Exception as e:
            print(f"Upload error: {str(e)}")
            flash(f'Error uploading file: {str(e)}')
            return redirect(url_for('index'))
    else:
        flash('Invalid file type. Allowed types: PNG, JPG, JPEG, GIF, TIFF, BMP')
        return redirect(url_for('index'))

if __name__ == '__main__':
    print("Starting Flask application...")
    print("Make sure OPENROUTER_API_KEY environment variable is set")
    app.run(debug=True)
