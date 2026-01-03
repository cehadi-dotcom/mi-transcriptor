import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from fpdf import FPDF
import re
import io

# --- Configuración de la página ---
st.set_page_config(page_title="YouTube a PDF", page_icon="📄")

# --- Funciones Auxiliares ---

def extract_video_id(url):
    """Extrae la ID limpia del video."""
    video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    return video_id.group(1) if video_id else None

def generate_pdf(text):
    """Genera el objeto PDF en memoria."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Título interno
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, 'Transcripción de Video', 0, 1, 'C')
    pdf.ln(10)
    
    # Cuerpo del texto
    pdf.set_font("Arial", size=11)
    
    # FPDF básico necesita codificación latin-1 para tildes y ñ
    # Reemplazamos caracteres no soportados para evitar errores
    text_safe = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, text_safe)
    
    # Retornar el contenido del PDF como bytes string
    return pdf.output(dest='S').encode('latin-1')

# --- Interfaz de Usuario (Frontend) ---

st.title("📄 Descargador tipo Anthiago")
st.markdown("Pega una URL de YouTube para descargar su transcripción en **PDF**.")

url = st.text_input("URL del video de YouTube:")

if url:
    video_id = extract_video_id(url)
    
    if not video_id:
        st.error("❌ La URL no parece válida.")
    else:
        try:
            with st.spinner('Extrayendo subtítulos...'):
                # Busca subtítulos en español, si no hay, busca en inglés
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['es', 'en'])
                
                # Formatear a texto plano
                formatter = TextFormatter()
                text_formatted = formatter.format_transcript(transcript)
                
                # Mostrar una vista previa del texto en la web
                with st.expander("Ver vista previa del texto"):
                    st.text_area("Texto extraído:", text_formatted, height=200)

                # Generar el PDF en memoria
                pdf_bytes = generate_pdf(text_formatted)
                
                # Botón de descarga
                st.download_button(
                    label="⬇️ Descargar PDF",
                    data=pdf_bytes,
                    file_name=f"transcripcion_{video_id}.pdf",
                    mime="application/pdf"
                )
                
        except Exception as e:
            st.error("⚠️ No se pudieron extraer los subtítulos.")
            st.info("Posibles causas: El video no tiene subtítulos/CC activados o es un video privado.")
            # st.exception(e) # Descomentar para ver el error técnico exacto