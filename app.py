# Lib do servidor
from flask import Flask, request, render_template, send_from_directory
# Lib processamento imagens
import cv2
import numpy as np
import os

# Criando instância
app = Flask(__name__)
# diretório onde o arquivo de imagem é carregado e processado
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# rota principal do app
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        # Verifica se recebeu a imagem
        if 'file' not in request.files:
            return 'Nenhum arquivo enviado'
        file = request.files['file']
        if file.filename == '':
            return 'Nenhum arquivo selecionado'

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Carregando a imagem com OpenCv
        img = cv2.imread(filepath)
        if img is None:
            return 'Erro ao carregar imagem'

        # Salvar a imagem original no diretório static
        original_path = os.path.join(STATIC_FOLDER, 'original_' + file.filename)
        cv2.imwrite(original_path, img)

        # Aplica os efeitos selecionados
        if 'sharpen' in request.form:
            kernel_sharpening = np.array([
                [0, -1, 0],
                [-1, 5, -1],
                [0, -1, 0]
            ])
            img = cv2.filter2D(img, -1, kernel_sharpening)

        if 'blur' in request.form:
            img = cv2.GaussianBlur(img, (17, 17), 0)

        if 'rotate' in request.form:
            (h, w) = img.shape[:2]
            center = (w / 2, h / 2)
            matrix = cv2.getRotationMatrix2D(center, 45, 1.0)
            img = cv2.warpAffine(img, matrix, (w, h))

        # Salvando a imagem processada
        result_path = os.path.join(STATIC_FOLDER, 'processed_' + file.filename)
        cv2.imwrite(result_path, img)

        # Renderiza 
        return render_template('index.html', original_filename='original_' + file.filename,
                               processed_filename='processed_' + file.filename)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)