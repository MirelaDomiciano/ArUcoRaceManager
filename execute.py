import cv2
import numpy as np
from datetime import datetime
import time
from collections import deque
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# Função para configurar a ArUco
def start_camera(cam_id = 0):
    cap = cv2.VideoCapture(cam_id)
    if not cap.isOpened():
        print("Erro em abrir a camera")
        exit()
    return cap

#Gera as arucos que podem do dicionário escolhido 
def generated_aruco():
    aruco_dict, param, detector = configure_aruco()
    size = 400
    for id in range(30):
        aruco_image = cv2.aruco.generateImageMarker(aruco_dict, id, size)
        cv2.imshow("Aruco Image", aruco_image)
        cv2.imwrite(f"makers/maker_{id}.png", aruco_image)
    #    cv2.waitKey(0)
    #    break

#Faz a configuração do dicionario e dos parametros das arucos
def configure_aruco():
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
    param = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, param)
    return aruco_dict, param, detector

#Faz a detecção das arucos e devolve o id da primeira aruco encontrada 
def detect_aruco(frame, detector, consecutive_frames):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    marker_corners, marker_IDs, reject = detector.detectMarkers(gray_frame)
    detected_id = None
    min_consecutives = 6

    if marker_corners:
        for ids, corners in zip(marker_IDs, marker_corners):
            corners = corners.astype(np.int32)
            corners = corners.reshape(-1, 1, 2)  # Corrigir a forma para (número de pontos, 1, 2)
            cv2.polylines(
                frame, [corners], True, (0, 255, 255), 4, cv2.LINE_AA
            )
            corners = corners.reshape(4, 2)
            corners = corners.astype(int)
            top_right = corners[0].ravel()
            top_left = corners[1].ravel()
            bottom_right = corners[2].ravel()
            bottom_left = corners[3].ravel()
            cv2.putText(
                frame, f"id: {ids[0]}", tuple(top_right), cv2.FONT_HERSHEY_PLAIN, 1.3, (200, 100, 0), 2, cv2.LINE_AA,
            )
            detected_id = ids[0]
            consecutive_frames += 1
    else:
        consecutive_frames = 0  # Zerar o contador se não houver detecção

    if consecutive_frames < min_consecutives:
        detected_id = None
    else:
        consecutive_frames = 0


    cv2.imshow('frame', frame)
    return detected_id, consecutive_frames

def read_csv(file_csv, time_start):
    categorias = []  # Lista para armazenar as categorias e suas respectivas colunas
    dict_corredores = {}

    with open(file_csv, newline='') as csvfile:
        leitor_csv = csv.reader(csvfile, delimiter=',')
    
        next(leitor_csv)  # Ignora a primeira linha
        headers = next(leitor_csv)  # Lê o cabeçalho e ignora
        j = 1
        for i, item in enumerate(headers):
            if i == j:  # Verifica se é uma coluna de categoria
                if item.strip():  # Verifica se a célula não está vazia
                    categorias.append((item, i))  # Armazena o nome da categoria e o índice da coluna
                else:
                    break
                j += 4

        next(leitor_csv)
        for categoria, cat_index in categorias:
            dict_corredores[categoria] = []  # Inicializa uma lista para os corredores desta categoria

        for linha in leitor_csv:
            for categoria, cat_index in categorias:
                nome = linha[cat_index]
                modelo_moto = linha[cat_index + 1]
                numero_moto = linha[cat_index + 2]
                if nome and modelo_moto and numero_moto:  # Verifica se todas as células estão preenchidas
                    corredor = {
                        'nome': nome,
                        'modelo_moto': modelo_moto,
                        'numero_moto': int(numero_moto),
                        'laps': 0,
                        'time_laps': [],
                        'last_detection': time_start,
                        'time_elapsed': 0
                    }
                    dict_corredores[categoria].append(corredor)

    return dict_corredores, categorias

#Ordena o dicionario de motos em uma lista e salva em um arquivo .txt a lista ordenada
def save_to_file(dict_corredores, time_start):
    dt_object = datetime.fromtimestamp(time_start)
    year = str(dt_object.year)
    month = str(dt_object.month).zfill(2)
    day = str(dt_object.day).zfill(2)
    hour = str(dt_object.hour).zfill(2)
    minutes = str(dt_object.minute).zfill(2)

    for categoria, corredores in dict_corredores.items():
        # Ordenar os corredores pelo número de voltas e, em caso de empate, pelo tempo do último registro
        sorted_corredores_list = sorted(corredores, key=lambda x: (-x['laps'], x['last_detection']))

        nome_arquivo = f'registros/{categoria}_{day}_{month}_{year}_{hour}_{minutes}.txt'
        file_info = f'registros/info_{categoria}_{day}_{month}_{year}_{hour}_{minutes}.txt'
        with open(nome_arquivo, 'w', encoding='utf-8') as file, open(file_info, 'w', encoding='utf-8') as info_file:
            posicao = 1
            info_file.write(f"----------------------------------------\n")
            info_file.write(f"              {categoria}               \n")

            file.write(f"----------------------------------------\n")
            file.write(f"              {categoria}               \n")

            for posicao, corredor in enumerate(sorted_corredores_list, start=1):
                time_total = int(corredor['last_detection']-time_start)
                hours_c = int(time_total / 3600)  # 3600 segundos em uma hora
                min_c = int((time_total % 3600) / 60)  # Resto da divisão inteira por 3600 segundos, dividido por 60 para obter os minutos
                seg_c = int(time_total % 60)  # Resto da divisão inteira por 60 segundos para obter os segundos

                if(corredor['laps'] == 0):
                    hours_c = 0
                    min_c = 0
                    seg_c = 0 

                file.write(f"----------------------------------------\n")
                file.write(f"{posicao}\u00b0 - #{corredor['numero_moto']} - {corredor['nome']} - {corredor['laps']} voltas - {str(hours_c).zfill(2)}:{str(min_c).zfill(2)}:{str(seg_c).zfill(2)}\n")
                info_file.write(f"----------------------------------------\n")
                info_file.write(f"{posicao}\u00b0 - #{corredor['numero_moto']} - {corredor['nome']}\n")

from datetime import datetime

def file_corredores(dict_corredores, time_start): 
    dt_object = datetime.fromtimestamp(time_start)
    year = str(dt_object.year)
    month = str(dt_object.month).zfill(2)
    day = str(dt_object.day).zfill(2)
    for categoria, corredores in dict_corredores.items():
        for corredor in corredores:
            name_file = f'tempo_pilotos/{corredor["nome"]}_{categoria}_{day}_{month}_{year}.txt'
            with open(name_file, 'w') as file:
                file.write(f"---------------------------------------\n")
                file.write(f'       Piloto {corredor["nome"]}       \n')
                file.write(f"---------------------------------------\n")
                for lap, lap_time in enumerate(corredor['time_laps'], start=1):
                    lap_time_hour = int(lap_time / 3600)  # 3600 segundos em uma hora
                    lap_time_min = int((lap_time % 3600) / 60)  # Resto da divisão inteira por 3600 segundos, dividido por 60 para obter os minutos
                    lap_time_seg = int(lap_time % 60)
                    file.write(f'{lap}\u00b0 volta - {str(lap_time_hour).zfill(2)}:{str(lap_time_min).zfill(2)}:{str(lap_time_seg).zfill(2)}\n')
                    file.write(f"---------------------------------------\n")


def file_corredores_pdf(dict_corredores, time_start):
    dt_object = datetime.fromtimestamp(time_start)
    year = str(dt_object.year)
    month = str(dt_object.month).zfill(2)
    day = str(dt_object.day).zfill(2)
    
    for categoria, corredores in dict_corredores.items():
        for corredor in corredores:
            name_file = f'tempo_pilotos/{corredor["nome"]}_{categoria}_{day}_{month}_{year}.pdf'

            # Criar o documento PDF
            doc = SimpleDocTemplate(name_file, pagesize=letter)
            styles = getSampleStyleSheet()
            style_heading = styles["Heading1"]
            style_normal = styles["BodyText"]

            # Estilo para informações de volta com tamanho de fonte maior
            style_lap_info = ParagraphStyle(
                name='LapInfo',
                parent=styles["BodyText"],
                fontSize=14
            )

            # Lista para armazenar os elementos do PDF
            elements = []

            # Adicionar cabeçalho
            header_text = f'Voltas piloto {corredor["nome"]}'
            header = Paragraph(header_text, style_heading)
            elements.append(header)
            elements.append(Spacer(1, 12))

            # Adicionar dados das voltas com estilo de fonte maior
            lap_data = []
            for lap, lap_time in enumerate(corredor['time_laps'], start=1):
                lap_time_hour = int(lap_time / 3600)
                lap_time_min = int((lap_time % 3600) / 60)
                lap_time_sec = int(lap_time % 60)
                lap_text = f'{lap}\u00b0 volta - {str(lap_time_hour).zfill(2)}:{str(lap_time_min).zfill(2)}:{str(lap_time_sec).zfill(2)}'
                lap_data.append(Paragraph(lap_text, style_lap_info))

            # Adicionar dados de volta ao PDF
            elements.extend(lap_data)

            # Construir o PDF
            doc.build(elements)
     
#Salva no arquivo quando a corrida é iniciada, pausada, retomada ou encerrada junto a seus respectivos tempos
def write(name, time, op):
    name_file = f'registros/corrida_{name}_registros.txt'
    with open(name_file, 'a') as file:
        file.write(f"{op} - {time}\n")

#Faz a inserção das motos no dicionario junto ao numero de voltas, o tempo da ultima detecção e os tempos das demais voltas
def register(id, dict_corredores, time_min, time_start):
    current_time = time.time()
    if id is not None:
        for categoria, corredores in dict_corredores.items():
            for corredor in corredores:
                if corredor['numero_moto'] == id and (current_time - corredor['last_detection'] > time_min or corredor['laps'] == 0):
                    corredor['laps'] += 1
                    corredor['time_laps'].append(current_time-corredor['last_detection'])
                    corredor['last_detection'] = current_time
                    time_elapsed_in_secconds = current_time - corredor['last_detection']
                    corredor['time_elapsed'] = f'{int(time_elapsed_in_secconds//60)}:{str(int(time_elapsed_in_secconds%60)).zfill(2)}'
                    print(f"Moto {id} completou a volta {corredor['laps']}")

    return dict_corredores

#Exibe o menu
def menu():
    print("Clique na janela que exibe a imagem da camera e pressione:\nf - Finalizar a corrida")

def main():
    cap = start_camera()
    aruco_dict, param, detector = configure_aruco()

    time_min = float(input("Digite o tempo mínimo para completar 1 volta em minutos: "))
    time_min *= 60

    file_csv = 'Cadastros.csv'
    op = input("Digite i para iniciar a corrida: ") 
    if op == "i":
        print(f'Corrida iniciada!')
        start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_start = time.time()
        dict_corredores, categorias = read_csv(file_csv, time_start)
        consecutives_frames = 0
        times_pressed = 0
        time_first_pressed = False     

        save_to_file(dict_corredores, time_start)

        menu()
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            #chama a detecção das arucos
            id, consecutives_frames = detect_aruco(frame, detector, consecutives_frames)
            #chama o registro no dicionário de motos
            if id is not None:
                dict_corredores = register(id, dict_corredores, time_min, time_start)
                save_to_file(dict_corredores, time_start)

            #possibilita a pausa, retomada e encerramento da corrida
            key = cv2.waitKey(1) & 0xFF  # Máscara para pegar apenas os últimos 8 bits
                        
            if key == ord("f"):
                times_pressed += 1
                time_first_pressed = time.time()
                if(times_pressed >= 2):
                    print("Corrida Encerrada")
                    #ordena e salva os dados no dicionario no arquivo
                    save_to_file(dict_corredores, time_start)
                    file_corredores_pdf(dict_corredores, time_start)
                    break

            if(time_first_pressed != False):
                if(time.time() - time_first_pressed > 0.3):
                    print('Passou')
                    times_pressed = 0
                    time_first_pressed = False

    cap.release()
    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    main()