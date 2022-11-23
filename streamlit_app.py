import streamlit as st
import pdf2image
import pdftotext

title = "PII Redaction GUI"
st.set_page_config(page_title=title)
st.title('History Lab ' + title)
uploaded_file = st.file_uploader('upload PDF', type=['pdf'])
# Store Pdf with convert_from_path function
if uploaded_file:
    images = pdf2image.convert_from_bytes(uploaded_file.getvalue())
    st.image(images[0])
    pdf = pdftotext.PDF(uploaded_file, physical=True)
    st.subheader("Extracted Text")
    st.code("\n\n".join(pdf))
    st.subheader("Redacted Text")
    st.subheader("Redacted PDF")
# for i in range(len(images)):
#    images[i].save('page' + str(i) +'.jpg', 'JPEG')




# st.markdown(f'<iframe src="https://drive.google.com/viewerng/viewer?\
# embedded=true&url=https://s3.documentcloud.org/documents/23315766/boa-zelle-lawsuit-ii.pdf"\
#  width="100%" height="900">', unsafe_allow_html=True)
