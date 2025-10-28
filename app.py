import smtplib
import pandas as pd
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import time

# Set up logging
logging.basicConfig(filename="email_log.txt", level=logging.DEBUG,
                   format="%(asctime)s - %(levelname)s - %(message)s")

#todo only one file
def attach_file(msg, filepath):
    try:
        with open(filepath, 'rb') as f:
            attachment = MIMEApplication(f.read())
            attachment.add_header('Content-Disposition', 'attachment', 
                                filename=os.path.basename(filepath))
            msg.attach(attachment)
            logging.info(f"File attached successfully: {filepath}")
    except Exception as e:
        logging.error(f"Error attaching file {filepath}: {e}")
        raise

#todo 2 attachment file
# First, modify the attach_file function to handle multiple files
# def attach_files(msg, filepaths):
#     if isinstance(filepaths, str):
#         filepaths = [filepaths]  # Convert single path to list
        
#     for filepath in filepaths:
#         try:
#             with open(filepath, 'rb') as f:
#                 attachment = MIMEApplication(f.read())
#                 attachment.add_header('Content-Disposition', 'attachment', 
#                                     filename=os.path.basename(filepath))
#                 msg.attach(attachment)
#                 logging.info(f"File attached successfully: {filepath}")
#         except Exception as e:
#             logging.error(f"Error attaching file {filepath}: {e}")
#             raise

# Then update the attachment section in the main loop
# # Assuming attachment_paths are comma-separated in your CSV
# if pd.notna(row.get('attachment_path')):
#     file_paths = row['attachment_path'].split(',')
#     attach_files(msg, file_paths)

# Update the email_template string with correct formatting
email_template = """
<html>
<head>
    <meta charset="UTF-8">
    <style>
body {{
    font-family: Noto Serif Khmer, Noto Serif Khmer;
    line-height: 1.6;
    color: #333333;
}}
.container {{
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
}}
.header {{
    color: #2c5282;
    font-size: 24px;
    margin-bottom: 20px;
}}
.content {{
    background-color: #f7fafc;
    padding: 15px;
    border-left: 4px solid #4299e1;
    margin: 15px 0;
}}
.details {{
    margin-top: 20px;
}}
.footer {{
    margin-top: 30px;
    color: #718096;
}}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">សូមគោរពជូន,<br>លោក លោកស្រី អ្នកនាង កញ្ញា សិក្ខាកាម,</div>
        
        <div class="content">
            <p>{custom_message}</p>
        </div>
        <div class="details">
            <p><strong>សម្រាប់ព័ត៌មានបន្ថែមសូមទំនាក់ទំនង:</strong> {contact}</p>
            <p><strong>លេខទូរស័ព្ទ:</strong> {number}</p>
        </div>
        <div class="footer">
            <p>Best regards,<br>
            The Accounting And Auditing Regulator Team</p>
        </div>
    </div>
</body>
</html>
"""


try:
    # Load contacts
    contacts = pd.read_csv("contacts.csv")
    logging.info(f"Successfully loaded {len(contacts)} contacts from CSV")

    # Email settings (Gmail for development)
    smtp_server = "smtp.gmail.com"
    port = 587
    sender_email = os.getenv('GMAIL_EMAIL', 'your-gmail@gmail.com')
    password = os.getenv('GMAIL_APP_PASSWORD', 'your-app-specific-password')

    with smtplib.SMTP(smtp_server, port, timeout=30) as server:
        server.starttls()
        server.login(sender_email, password)
        logging.info("Successfully logged into SMTP server")
        
        for index, row in contacts.iterrows():
            try:
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = row['email']
                msg['Subject'] = f"វគ្គបណ្តុះបណ្តាលស្តីពីថ្នាលរៀបចំរបាយការណ៍ហិរញ្ញវត្ថុឌីជីថល"
                
                # Format HTML content
                html_content = email_template.format(
                    name=row['name'],
                    custom_message=row['custom_message'],
                    contact=row['contact'],
                    number=row['number']
                )
                
                msg.attach(MIMEText(html_content, 'html'))
                
                # In the main email sending loop, update the attachment section:
                # Attach files if paths exist
                if pd.notna(row.get('attachment_path')):
                    attach_file(msg, row['attachment_path'])
                    
                if pd.notna(row.get('attachment_path2')):
                    attach_file(msg, row['attachment_path2'])

                    
                # Send email
                server.sendmail(sender_email, row['email'], msg.as_string())
                logging.info(f"Successfully sent email to {row['email']}")
                print(f"Email sent to {row['email']}")
                
                # Add delay between emails
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"Error sending email to {row['email']}: {e}")
                print(f"Failed to send email to {row['email']}")
                continue

except Exception as e:
    logging.error(f"Script error: {e}")
    print("An error occurred. Check email_log.txt for details")

print("Email sending process completed")