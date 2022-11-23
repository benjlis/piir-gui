import streamlit as st
import dataprofiler as dp
import os
import pdf2image
import pdftotext
import fitz

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # disable TensorFlow info msgs

title = "PII Redaction"
st.set_page_config(page_title=title, layout='wide')
st.title('History Lab ' + title)

# Configuration of DataProfiler
redacted = ['ADDRESS', 'BAN', 'CREDIT_CARD', 'UUID', 'HASH_OR_KEY',
            'IPV4', 'IPV6', 'MAC_ADDRESS', 'PERSON', 'PHONE_NUMBER', 'SSN',
            'URL', 'DRIVERS_LICENSE', 'DATE']
data_labeler = dp.DataLabeler(labeler_type='unstructured')
# Set the output to the NER format (start position, end position, label)
data_labeler.set_params(
    {'postprocessor': {'output_format': 'ner',
                       'use_word_level_argmax': True}})
uploaded_file = st.file_uploader('upload PDF', type=['pdf'])
# Store Pdf with convert_from_path function
if uploaded_file:
    # Convert uploaded PDF to jpg to get around streamlit weirdness
    images = pdf2image.convert_from_bytes(uploaded_file.getvalue())
    st.image(images[0])
    # Extract text from PDF and display
    pdf = pdftotext.PDF(uploaded_file, physical=True)
    text = "\n\n".join(pdf)
    st.subheader("Extracted Text")
    st.code(text)
    # Find text elements to redact
    st.subheader("Redacted Text")
    # Find the PII using the built-in model
    data = [text]
    results = data_labeler.predict(data)
    all_labels = results['pred'][0]
    redact_labels = list(filter(lambda l: l[2] in redacted, all_labels))
    # Display the text file with redactions applied
    orig_text = text
    redact_text = ''
    pos = 0
    redactions = list()
    sensitive = list()
    for s in redact_labels:
        r = list(s)
        r.append(orig_text[r[0]:r[1]])
        sensitive.append(orig_text[r[0]:r[1]])
        redactions.append(r)
        redact_text += orig_text[pos:r[0]] + '**' + r[2] + '**'
        pos = r[1]
    redact_text += orig_text[pos:]
    st.json(redactions, expanded=False)
    st.code(redact_text)
    st.subheader("Redacted PDF")
    rdoc = fitz.Document(stream=uploaded_file.getvalue())
    for page in rdoc:
        # _wrapContents is needed for fixing
        # alignment issues with rect boxes in some
        # cases where there is alignment issue
        page.wrap_contents()
        # getting the rect boxes which consists the matching email regex
        for data in sensitive:
            areas = page.search_for(data)
            # drawing outline over sensitive datas
            _ = [page.add_redact_annot(area, fill=(0, 0, 0)) for area in areas]
            # applying the redaction
            page.apply_redactions()
    # rdoc.save('redacted-' + uploaded_file.name)
    images = pdf2image.convert_from_bytes(rdoc.tobytes())
    st.image(images[0])
    st.download_button(label='Download redacted PDF',
                       data=rdoc.tobytes(),
                       file_name='redacted-' + uploaded_file.name,
                       mime='application/pdf')
