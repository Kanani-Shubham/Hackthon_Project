from flask import Flask, render_template_string, request, jsonify, send_file
from model import TenderGenerator
from data_manager import TenderDataManager
from database import db, TenderDocument
from pdf_generator import TenderPDFGenerator
from datetime import datetime
import os
import gc
import psutil
import torch
import torch
from content_processor import ContentProcessor

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'generated_pdfs'

db.init_app(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists('generated_pdfs'):
    os.makedirs('generated_pdfs')

with app.app_context():
    db.create_all()

HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tender Document Generator</title>
    <style>
        body {
            font-family: 'Google Sans', Roboto, Arial, sans-serif;
            background-color: #f0f0f0;
            margin: 0;
            padding: 20px;
            color: #202124;
        }
        .form-container {
            max-width: 770px;
            margin: 12px auto;
            background: #fff;
            padding: 24px;
            border-radius: 8px;
            box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 2px 6px 2px rgba(60,64,67,0.15);
        }
        .form-header {
            text-align: left;
            margin-bottom: 24px;
            border-top: 10px solid #673ab7;
            padding-top: 12px;
        }
        .form-header h1 {
            color: #202124;
            font-size: 32px;
            margin-bottom: 12px;
            font-weight: 400;
        }
        .form-header p {
            color: #202124;
            font-size: 14px;
            margin-top: 0;
        }
        .form-group {
            margin-bottom: 24px;
            background: #fff;
            padding: 24px;
            border-radius: 8px;
            border: 1px solid #dadce0;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-family: Roboto, Arial, sans-serif;
            font-size: 16px;
            font-weight: 500;
            color: #202124;
        }
        .form-group input, .form-group textarea, .form-group select {
            width: calc(100% - 24px);
            padding: 12px;
            border: 1px solid #dadce0;
            border-radius: 4px;
            font-size: 14px;
            color: #202124;
            transition: border 0.2s;
        }
        .form-group input:focus, .form-group textarea:focus {
            border: 2px solid #673ab7;
            outline: none;
        }
        .form-group textarea {
            resize: vertical;
            min-height: 80px;
        }
        .submit-button {
            background-color: #673ab7;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-family: 'Google Sans', sans-serif;
            font-size: 14px;
            font-weight: 500;
            letter-spacing: 0.25px;
            transition: background-color 0.2s;
            float: right;
            margin-right: 24px;
        }
        .submit-button:hover {
            background-color: #5829b5;
        }
        .submit-button:active {
            background-color: #452788;
        }
        input:required + label::after, textarea:required + label::after {
            content: "*";
            color: #d93025;
            margin-left: 4px;
        }
        @media (max-width: 768px) {
            .form-container {
                margin: 0;
                padding: 16px;
            }
            .form-group {
                padding: 16px;
            }
        }
        
        .loader {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(255, 255, 255, 0.9);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        
        .loader-content {
            text-align: center;
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #673ab7;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .download-section {
            display: none;
            max-width: 770px;
            margin: 24px auto;
            background: #fff;
            padding: 24px;
            border-radius: 8px;
            box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 2px 6px 2px rgba(60,64,67,0.15);
        }
        .download-button {
            background-color: #34a853;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-family: 'Google Sans', sans-serif;
            font-size: 14px;
            font-weight: 500;
            letter-spacing: 0.25px;
            transition: background-color 0.2s;
            text-decoration: none;
            display: inline-block;
        }
        .download-button:hover {
            background-color: #2d9147;
        }
    </style>
</head>
<body>
    <div class="loader">
        <div class="loader-content">
            <div class="spinner"></div>
            <p>Generating Tender Document...</p>
        </div>
    </div>
    
    <div class="form-container">
        <div class="form-header">
            <h1>Tender Document Generator</h1>
            <p>Fill out the tender details below</p>
        </div>
        <form id="tenderForm" onsubmit="generatePDF(event)">
            <div class="form-group">
                <label for="tender_title">Tender Title</label>
                <input type="text" id="tender_title" name="tender_title" required>
            </div>
            <div class="form-group">
                <label for="issuing_authority">Issuing Authority</label>
                <input type="text" id="issuing_authority" name="issuing_authority" required>
            </div>
            <div class="form-group">
                <label for="tender_amount">Tender Amount (₹)</label>
                <input type="number" id="tender_amount" name="tender_amount" required>
            </div>
            <div class="form-group">
                <label for="bid_start_date">Bid Start Date</label>
                <input type="date" id="bid_start_date" name="bid_start_date" required>
            </div>
            <div class="form-group">
                <label for="bid_end_date">Bid End Date</label>
                <input type="date" id="bid_end_date" name="bid_end_date" required>
            </div>
            <div class="form-group">
                <label for="eligibility_criteria">Eligibility Criteria</label>
                <textarea id="eligibility_criteria" name="eligibility_criteria" rows="4" required></textarea>
            </div>
            <div class="form-group">
                <label for="scope_of_work">Scope of Work</label>
                <textarea id="scope_of_work" name="scope_of_work" rows="4" required></textarea>
            </div>
            <div class="form-group">
                <label for="requirements">Requirements</label>
                <textarea id="requirements" name="requirements" rows="4" required></textarea>
            </div>
            <div class="form-group">
                <label for="contact_details">Contact Details</label>
                <textarea id="contact_details" name="contact_details" rows="4" required></textarea>
            </div>
            <div class="form-group">
                <label for="mvp_details">MVP (Minimum Viable Product)</label>
                <textarea id="mvp_details" name="mvp_details" rows="4" required></textarea>
            </div>
            <div class="form-group">
                <label for="milestone_deliverables">Immediate Milestone Deliverables</label>
                <textarea id="milestone_deliverables" name="milestone_deliverables" rows="4" required></textarea>
            </div>
            <div class="form-group">
                <label for="liquidated_damages">Liquidated Damages</label>
                <textarea id="liquidated_damages" name="liquidated_damages" rows="4" required></textarea>
            </div>
            <button type="submit" class="submit-button">Generate PDF</button>
        </form>
    </div>
    
    <div id="downloadSection" class="download-section">
        <h2 style="color: #202124; margin-bottom: 20px;">Generated Document</h2>
        <p style="margin-bottom: 20px;">Your tender document has been generated successfully!</p>
        <a id="downloadButton" href="#" class="download-button">
            Download Tender Document
        </a>
    </div>

    <script>
        function generatePDF(event) {
            event.preventDefault();
            
            // Show loader
            document.querySelector('.loader').style.display = 'flex';
            
            // Get form data
            const formData = new FormData(event.target);
            
            // Send request
            fetch('/generate_pdf', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    // Show download section
                    const downloadSection = document.getElementById('downloadSection');
                    const downloadButton = document.getElementById('downloadButton');
                    downloadSection.style.display = 'block';
                    downloadButton.href = `/download_pdf/${data.tender_id}`;
                    
                    // Scroll to download section
                    downloadSection.scrollIntoView({ behavior: 'smooth' });
                }
            })
            .catch(error => {
                alert('Error generating PDF: ' + error);
            })
            .finally(() => {
                // Hide loader
                document.querySelector('.loader').style.display = 'none';
            });
        }
    </script>
</body>
</html>
"""

def clear_memory():
    try:
        if hasattr(torch, 'cuda'):
            torch.cuda.empty_cache()
    except ImportError:
        pass  # If torch is not installed, simply skip clearing CUDA cache
        torch.cuda.empty_cache()

@app.route('/')
def form():
    return render_template_string(HTML_FORM)

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    try:
        clear_memory()
        
        tender_data = {
            "tender_title": request.form['tender_title'],
            "issuing_authority": request.form['issuing_authority'],
            "tender_amount": float(request.form['tender_amount']),
            "bid_start_date": datetime.strptime(request.form['bid_start_date'], '%Y-%m-%d').date(),
            "bid_end_date": datetime.strptime(request.form['bid_end_date'], '%Y-%m-%d').date(),
            "eligibility_criteria": request.form['eligibility_criteria'],
            "scope_of_work": request.form['scope_of_work'],
            "requirements": request.form['requirements'],
            "contact_details": request.form['contact_details'],
            "mvp_details": request.form['mvp_details'],
            "milestone_deliverables": request.form['milestone_deliverables'],
            "liquidated_damages": request.form['liquidated_damages'],
            "tender_id": f"TEN{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }

        generator = TenderGenerator()
        generated_content = generator.generate_tender_content(tender_data)
        
        # Clean the content before saving and generating PDF
        processed_content = ContentProcessor.clean_content(generated_content)
        
        data_manager = TenderDataManager()
        tender_doc = data_manager.save_tender_data(tender_data, processed_content)

        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{tender_data["tender_id"]}.pdf')
        pdf_generator = TenderPDFGenerator(pdf_path)
        pdf_generator.generate_pdf(tender_data, processed_content)
        
        tender_doc.pdf_path = pdf_path
        db.session.commit()

        clear_memory()
        return jsonify({
            'success': True,
            'tender_id': tender_data['tender_id'],
            'title': tender_data['tender_title'],
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    except Exception as e:
        clear_memory()
        return jsonify({'error': str(e)}), 500

@app.route('/download_pdf/<tender_id>')
def download_pdf(tender_id):
    tender_doc = TenderDocument.query.filter_by(tender_id=tender_id).first_or_404()
    return send_file(tender_doc.pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)