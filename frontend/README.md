# SmartContractor

**Automated Contract Processing with AI-Powered Data Extraction**

---

## 📖 Overview

SmartContractor is an end-to-end solution designed to streamline contract processing by combining AI-driven data extraction with human oversight. The system automates the extraction of key contract details, validates accuracy through user interaction, and generates finalized PDFs—reducing manual effort while maintaining precision.

---

## ✨ Key Features

- **Document Classification**: Automatically identifies contract type.
- **LLM/NLP Data Extraction**: Extracts entities (company name, ID, dates, items, pricing).
- **User Validation Interface**: Confirm/Correct extracted data via web UI.
- **Human-in-the-Loop Editing**: Manual fixes when AI results need adjustment.
- **PDF Generation**: Produce downloadable/email-ready contracts.
- **Iterative Processing**: Cycles until user confirms all data is accurate.

---

## 🏗️ Architecture Overview

The system consists of several key components that work together to automate and streamline the document extraction and validation process:

### Web Interface (UI)
- Users can upload vendor contract files through the web interface
- The UI provides a simple way for users to interact with the system

### File Storage Layer
- Uploaded files are temporarily stored in a file storage layer for further processing

### Document Classification Module
- The document classification module identifies the type of contract (e.g., vendor contract) based on the contents of the uploaded document

### Data Extraction (LLM/NLP)
This module uses a language model (LLM) and NLP techniques to extract key data from the contract, such as:
- Company Name
- Company ID
- Date, Item List
- Quantity, Price, and Total

### Confirmation from User
- The user is prompted to confirm the extracted data or request edits
- The system ensures the user can review the extracted details and make corrections if necessary

### Human in the Loop (if necessary)
- If the user requests edits, a human operator may manually fix the extracted data before the document is processed

### Final PDF Generation
- Once the data is confirmed, a PDF containing the extracted details is generated
- The user is given the option to download it or send it via email

### System Architecture
```plaintext
                         +------------------------------+
                         |       Web Interface (UI)     |
                         |  (User uploads vendor file)  |
                         +--------------+---------------+
                                        |
                                        v
                         +--------------+---------------+
                         |       File Storage Layer      |
                         | (Temporary input file storage)|
                         +--------------+---------------+
                                        |
                                        v
                         +--------------+---------------+
                         | Document Classification Module|
                         | (Which contract type is it?)  |
                         +--------------+---------------+
                                        |
                                        v
                         +--------------+---------------+
                         |   Data Extraction (LLM/NLP)   |
                         | - Company Name                |
                         | - Company ID                  |
                         | - Date, Item List             |
                         | - Quantity, Price, Total      |
                         +--------------+---------------+
                                        |
                                        v
                         +--------------+---------------+
                         |     Confirmation from User    |
                         | ("Is everything correct?")    |
                         +--------------+---------------+
                                        |
                      /-----------------+-----------------------\
                     /                  |                        \
                    v                   v                         v
        [Everything OK]      +-----------+------------+     [User Requests Edits]        
               |             |    Human in the loop   |                |
               v             |(Manually fix the Data) |                v
        [Generate PDF] <-----+-----------+------------+       +---------------------------+
              |                                               |   Get User Comments        |
          ----+----                                           | (Text instructions / fixes)|
         /         \                                          +------------+--------------+
        /           \                                                      |
[Download PDF]    [Send PDF to Email]                                      v
       |                 |                                     +------------+--------------+
        \               /                                      | Combine Extracted Data    |
         \             /                                       |   with User Comments      |
          v           v                                        +------------+--------------+
       [Process Complete]                                                   |
                                                                            v
                                                               +------------+--------------+
                                                               | Data Extraction (LLM/NLP) |
                                                               |    with user comments     |
                                                               +------------+--------------+
                                                                            |
                                                                            v
                                                               +------------+--------------+
                                                               | Re-send New Extracted     |
                                                               |         Entities          |
                                                               +------------+--------------+
                                                                            |
                                                                            └────> Repeat Until Confirmed

```


## 🛠️ Technologies Used
- **Docker**: For containerizing the application and ensuring consistent deployment across different environments.
- **Python**: The core language used for the backend processing.
- **streamlit**: For building the web interface and user interaction.
- **weasyprint**: For converting the extracted data into a downloadable PDF.
- **jinja2**: For rendering the final PDF templates.
- **python-docx**: For handling and processing Word documents (if required).
- **openpyxl**: For processing Excel files, if required.
- **PyPDF2**: For PDF file manipulation and extraction tasks.
- **boto3**: For integration with AWS services (e.g., file storage, Lambda).
- **Amazon Bedrock LLM**: For leveraging advanced NLP and language model capabilities for document classification and data extraction.

## 📋 Usage
1. **Upload Documents**
* Access the web interface and upload a contract document
* Supported formats: PDF, DOCX, DOC
2. **Review Extracted Data**
* The system will automatically extract key information
* Review the extracted data for accuracy
3. **Validate or Edit Data**
* Confirm if the extraction is correct
* Make edits if needed or request human intervention
4. **Generate PDF**
* Once data is confirmed, generate the final PDF
* Download the document or send via email

## License
This project is licensed under the Azercell.