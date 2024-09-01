import streamlit as st
import requests
from io import BytesIO
import PyPDF2
import anthropic

# Initialize the Claude AI client with the provided API key
api_key = st.secrets['api_key']
client = anthropic.Anthropic(api_key=api_key)

# Function to extract text from an online PDF
def extract_pdf_text(pdf_url):
    try:
        # Fetch the PDF content from the URL
        response = requests.get(pdf_url)
        response.raise_for_status()  # Check if the request was successful
        
        # Ensure the content type is 'application/pdf'
        if response.headers['Content-Type'] != 'application/pdf':
            raise ValueError("URL did not point to a PDF file")

        # Read the PDF content using PyPDF2
        pdf_reader = PyPDF2.PdfReader(BytesIO(response.content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the PDF file: {e}")
        return ""
    except PyPDF2.errors.PdfReadError as e:
        st.error(f"Error reading the PDF file: {e}")
        return ""
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return ""

# Function to find plant information in the PDF text
def find_plant_info(plant_name, pdf_text):
    # Basic keyword search; you can enhance this with NLP techniques
    if plant_name.lower() in pdf_text.lower():
        start = pdf_text.lower().find(plant_name.lower())
        end = pdf_text.find("\n", start + 500)  # Assuming relevant info is within 500 chars
        return pdf_text[start:end].strip()
    return "No specific information found for this plant."

# Streamlit app
st.title("Plant Care Information")

st.write("""
Enter the name of the plant to retrieve care information from the PDF and get detailed care instructions using Claude AI.
""")

# Input field for the plant name
plant_name = st.text_input("Enter the plant name:")

# URL of the PDF
pdf_url = "https://www.kellogggarden.com/wp-content/uploads/2020/05/Monthly-Flower-Gardening-Guide.pdf"

# Extract text from the PDF
pdf_text = extract_pdf_text(pdf_url)

# Display the plant care information
if st.button("Get Plant Care Information"):
    if plant_name and pdf_text:
        plant_info = find_plant_info(plant_name, pdf_text)
        
        if plant_info != "No specific information found for this plant.":
            # Create the prompt for Claude AI
            prompt = f"I have the following information about the plant {plant_name}:\n\n{plant_info}\n\nPlease provide detailed care instructions based on this information."
            
            # Call Claude AI API
            try:
                message = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=250,
                    temperature=0.7,
                    system="Use the information about the plant in the prompt to give tips on plant care, specifically water, soil and any other information",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                # Display the response from Claude AI
                useful_text = message['content'][0]['text']
                # st.text_area("Plant Care Instructions", value=message, height=300)
                # st.markdown(message)
            except Exception as e:
                st.error(f"An error occurred while calling Claude AI: {e}")
        else:
            st.warning(plant_info)
    else:
        st.warning("Please enter a plant name and ensure the PDF is accessible.")

