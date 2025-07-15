import streamlit as st
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os
import pandas as pd

# 🔹 Ler o Excel com os alojamentos
df = pd.read_excel("alojamentos.xlsx")

# Função para obter o nome a partir do registo
def obter_nome_do_registo(registo):
    resultado = df[df['Registo'].astype(str).str.strip() == str(registo).strip()]
    if not resultado.empty:
        return str(resultado.iloc[0]['Nome'])
    return "Desconhecido"

# Função para gerar PDF personalizado
def gerar_pdf(email, registo, nome):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Inserir imagem (opcional)
    imagem_path = "logo.png"
    if os.path.exists(imagem_path):
        pdf.image(imagem_path, x=10, y=8, w=50)
        pdf.ln(40)
    else:
        pdf.cell(200, 10, txt="BILHETE DIGITAL", ln=True, align="C")
        pdf.ln(10)

    # Cabeçalho
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="FICA QUE COMPENSA", ln=True, align="C")
    pdf.ln(8)

    # Informações do visitante
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"NOME DO ESTABELECIMENTO: {nome}", ln=True)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Email: {email}", ln=True)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="TERRAS DE BOURO", ln=True)

    pdf.set_font("Arial", 'I', 11)
    pdf.cell(200, 10, txt="NO CORAÇÃO DA NATUREZA", ln=True)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True)
    pdf.ln(10)

    # Benefícios
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Este bilhete dá desconto em:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="* Museu do Geira - Entrada Grátis", ln=True)
    pdf.cell(200, 10, txt="* Museu de Vilarinho da Furna - Entrada Grátis", ln=True)
    pdf.cell(200, 10, txt="* Embarcação Rio Caldo - 50% (sujeito a reserva e disponibilidade)", ln=True)

    os.makedirs("pdfs", exist_ok=True)
    # Sanear o nome do ficheiro
    registo_limpo = "".join(c for c in registo if c.isalnum() or c in ('-_'))
    email_limpo = email.replace('@', '_').replace('.', '_')
    caminho_pdf = f"pdfs/checkin_{email_limpo}_{registo_limpo}.pdf"
    pdf.output(caminho_pdf)
    return caminho_pdf


# Função para enviar email com o PDF em anexo
def enviar_email(email_destino, caminho_pdf):
    msg = EmailMessage()
    msg['Subject'] = 'Confirmação de Check-in'
    msg['From'] = 'teuemail@gmail.com'
    msg['To'] = email_destino
    msg.set_content("Olá!\n\nEm anexo segue o comprovativo da tua visita ao local.\n\nCumprimentos.")

    with open(caminho_pdf, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=os.path.basename(caminho_pdf))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('pfparantes@gmail.com', 'tsqn jwva cyll apxk')
        smtp.send_message(msg)

# Streamlit App
st.set_page_config(page_title="Check-in QR", page_icon="📍")

# Capturar o registo da URL (ex: ?registo=AL12345)
registo = st.query_params.get("registo", "Desconhecido")
nome = obter_nome_do_registo(registo)

# Apresentar na interface
st.title("📍 Check-in no Local")
st.write(f"Local identificado: **{registo} – {nome}**")
st.write("Por favor, introduz o teu e-mail para receberes o comprovativo em PDF.")

email = st.text_input("✉️ E-mail")

if st.button("Enviar Comprovativo por E-mail"):
    if email and "@" in email:
        caminho_pdf = gerar_pdf(email, registo, nome)
        enviar_email(email, caminho_pdf)
        st.success("✅ E-mail enviado com sucesso!")
    else:
        st.warning("Por favor, introduz um e-mail válido.")