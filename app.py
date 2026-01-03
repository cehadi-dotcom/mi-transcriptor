import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from fpdf import FPDF
import re

# --- Configuración de la página ---
st.set_page_config(page_title="YouTube a PDF Pro", page_icon="📄")

# --- Funciones ---

def extract_video_id(url):
    # Esta función saca el ID del video (ej: dQw4w9WgXcQ)
    video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    return video_id.group(1) if video_id else None

def generate_pdf(text, video_title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Título del PDF
    pdf.set_font("Arial", 'B', 14)
    # Limpiamos el título para evitar errores de caracteres raros
    title_safe = video_title.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, f"Transcripción: {title_safe}", 0, 'C')
    pdf.ln(5)
    
    # Cuerpo del texto
    pdf.set_font("Arial", size=11)
    # Limpieza agresiva de caracteres para que no falle el PDF
    text_safe = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, text_safe)
    
    return pdf.output(dest='S').encode('latin-1')

# --- Interfaz (Lo que ves en pantalla) ---

st.title("📄 Descargador tipo Anthiago")
st.markdown("Este descargador es **inteligente**: busca cualquier subtítulo y lo traduce a español si es necesario.")

url = st.text_input("Pega el link de YouTube aquí:")

if st.button("Buscar Transcripción"):
    if not url:
        st.warning("⚠️ Por favor, pega una URL primero.")
    else:
        video_id = extract_video_id(url)
        
        if not video_id:
            st.error("❌ Link no válido.")
        else:
            try:
                with st.spinner('Buscando y traduciendo subtítulos...'):
                    # 1. Obtener la lista de todos los subtítulos disponibles
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    
                    # 2. Intentar buscar uno en español, o tomar el primero que haya (inglés, generado auto, etc)
                    try:
                        # Intenta buscar manual en español o inglés
                        transcript = transcript_list.find_transcript(['es', 'en'])
                    except:
                        # Si falla, agarra CUALQUIERA (incluso los automáticos)
                        transcript = transcript_list.find_generated_transcript(['en', 'es'])
                    
                    # 3. TRADUCIR A ESPAÑOL (La magia de Anthiago)
                    # Esto fuerza a que, sea lo que sea, nos lo de en español
                    translated_transcript = transcript.translate('es')
                    
                    # 4. Convertir a texto plano
                    formatter = TextFormatter()
                    text_formatted = formatter.format_transcript(translated_transcript.fetch())

                    # Mostrar texto en pantalla
                    st.success("✅ ¡Transcripción encontrada!")
                    with st.expander("👀 Leer texto aquí"):
                        st.write(text_formatted)

                    # 5. Botón para descargar PDF
                    pdf_bytes = generate_pdf(text_formatted, video_id)
                    
                    st.download_button(
                        label="⬇️ Descargar PDF ahora",
                        data=pdf_bytes,
                        file_name=f"transcripcion_{video_id}.pdf",
                        mime="application/pdf"
                    )

            except Exception as e:
                # Si entra aquí, es que YouTube bloqueó la conexión o el video no tiene audio texto.
                st.error("❌ Error: No se pudo extraer.")
                st.info("Posibles causas:\n1. El video es muy nuevo o privado.\n2. YouTube bloqueó temporalmente tu conexión (espera un rato).")
