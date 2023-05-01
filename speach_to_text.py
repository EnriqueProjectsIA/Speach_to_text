from pydub import AudioSegment
from moviepy.editor import VideoFileClip
import os
from dotenv import load_dotenv
from typing import List, Dict
import openai
from html import unescape

class SpeechToText:
    """
    Clase para transcribir archivos de audio utilizando la API de OpenAI.
    
    Atributos:
        path_to_file (str): Ruta al directorio donde se encuentra el archivo de audio.
        list_of_files (List[str]): Lista de archivos en el directorio especificado.
        openai_key (str): Clave de API de OpenAI.
    """
    def __init__(self, path_to_file:str) -> None:
        """
        Inicializa una instancia de la clase SpeechToText.
        
        Args:
            path_to_file (str): Ruta al directorio donde se encuentra el archivo de audio.
        """
        self.path_to_file = path_to_file
        self.list_of_files = [file for file in os.listdir(self.path_to_file)]
        load_dotenv()
        self.openai_key = os.getenv('OPENAI_API_KEY')
    
    def print_files_and_index(self) -> None:
        """
        Imprime los nombres de los archivos en el directorio y sus índices correspondientes.
        """
        for index, file in enumerate(self.list_of_files):
            print(f'{index}: {file}')

    def select_file(self,full_file_path:str = None, file_name:str = None, index_file:int = None) -> str:
        """
        Selecciona un archivo de audio de la lista de archivos en el directorio.

        Args:
            file_name (str): Nombre del archivo de audio a segmentar (opcional).
            index_file (int): Índice del archivo a seleccionar.

        Returns:
            str: Nombre del archivo seleccionado.
        """
        if file_name is not None and index_file is not None and full_file_path is not None:
            raise Exception('You must pass a file name or an index or a full file path')
        elif file_name is None and full_file_path is None:
            full_path_to_file = os.path.join(self.path_to_file,self.list_of_files[index_file])
        elif file_name is not None and full_file_path is None and index_file is None:
            full_path_to_file = os.path.join(self.path_to_file,file_name)
        else:
            full_path_to_file = full_file_path        
        return full_path_to_file
    
    def extract_audio_from_video(self,full_file_path:str = None, file_name:str = None, index_file:int = None, path_to_save:str = None) -> None:
            
            input_video = self.select_file(full_file_path, file_name, index_file)
            output_file_name = os.path.basename(input_video).split('.')[0] + '.mp3'
            if path_to_save is None:
                output_audio = os.path.join(self.path_to_file, output_file_name)
            else:
                if not os.path.exists(path_to_save):
                    os.mkdir(path_to_save)
                output_audio = os.path.join(path_to_save, output_file_name)

            # Cargar el archivo de video
            video = VideoFileClip(input_video)

            # Extraer el audio del video
            audio = video.audio

            # Guardar el audio en un archivo
            audio.write_audiofile(output_audio)

            # Cerrar los objetos VideoFileClip y AudioClip para liberar recursos
            video.close()
            audio.close()

    
    def segment_audio(self, file_name = None, index_file = None, interval:int = 5, path_to_save:str = None) -> None:
        """
        Segmenta un archivo de audio en segmentos más pequeños de la duración especificada.

        Args:
            file_name (str): Nombre del archivo de audio a segmentar (opcional).
            index_file (int): Índice del archivo de audio a segmentar (opcional).
            interval (int): Duración en minutos de cada segmento (por defecto: 5).
            path_to_save (str): Ruta donde se guardarán los segmentos de audio (opcional).
        """
        

        if file_name is None and index_file is None:
            raise Exception('You must pass a file name or an index')
        
        if file_name is not None and index_file is not None and path_to_save is not None:
            full_file_name = os.path.join(self.path_to_file,path_to_save,file_name)
        elif file_name is None:
            full_file_name = os.path.join(self.path_to_file,self.list_of_files[index_file])
        else:
            full_file_name = os.path.join(self.path_to_file,file_name)
        
        if full_file_name.endswith('.mp3'):
            audio = AudioSegment.from_mp3(full_file_name)
            audio_format_type = 'mp3'
        elif full_file_name.endswith('.wav'):
            audio = AudioSegment.from_wav(full_file_name)
            audio_format_type = 'wav'
        else:
            raise Exception('File format not supported')


        if path_to_save is None:
            if not os.path.exists(os.path.join(self.path_to_file, self.list_of_files[index_file].split('.')[0])):
                path_to_save = os.path.join(self.path_to_file, self.list_of_files[index_file].split('.')[0])
                os.mkdir(path_to_save)
            else:
                path_to_save = os.path.join(self.path_to_file, self.list_of_files[index_file].split('.')[0])
        else:
            path_to_save = os.path.join(self.path_to_file, path_to_save)

        start_time = 0
        end_time = interval * 1000 * 60
        generated_files = []
        segment_name = os.path.basename(path_to_save)

        while start_time < len(audio):
            end_time = min(end_time, len(audio))
            audio_segment = audio[start_time:end_time]        
            output_file = os.path.join(path_to_save, f'{segment_name}_{start_time}-{end_time}.{audio_format_type}')
            audio_segment.export(output_file, format=audio_format_type)
            generated_files.append(output_file)
            start_time = end_time
            end_time += interval * 1000 * 60

        return (generated_files, path_to_save)

    def _check_file_size(self, file_path: str, max_size:int = 20000000) -> bool:
        """
        Verifica si el tamaño de un archivo está dentro del límite especificado.

        Args:
            file_path (str): Ruta al archivo cuyo tamaño se verificará.
            max_size (int): Tamaño máximo permitido en bytes (por defecto: 20000000 o 20MB aprox.).

        Returns:
            bool: True si el tamaño del archivo está dentro del límite, False en caso contrario.
        """
        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            return False
        else:
            return True
    
    def _check_all_file_sizes(self, files:List[str], max_size:int = 20000000) -> bool:
        """
        Verifica si el tamaño de todos los archivos en una lista está dentro del límite especificado.

        Args:
            files (List[str]): Lista de rutas a los archivos cuyos tamaños se verificarán.
            max_size (int): Tamaño máximo permitido en bytes (por defecto: 20000000).

        Returns:
            bool: True si el tamaño de todos los archivos está dentro del límite, False en caso contrario.
        """
        for file in files:
            if not self._check_file_size(file, max_size):
                return False
        return True

    def recursive_segment_audio(self, file_name=None, index_file=None, interval:int=5, path_to_save:str = None) -> None:
        """
        Segmenta recursivamente un archivo de audio en segmentos más pequeños de la duración especificada, asegurándose de que
        cada segmento esté dentro del límite de tamaño permitido por la API de OpenAI.

        Args:
            file_name (str): Nombre del archivo de audio a segmentar (opcional).
            index_file (int): Índice del archivo de audio a segmentar (opcional).
            interval (int): Duración en minutos de cada segmento (por defecto: 5).
            path_to_save (str): Ruta donde se guardarán los segmentos de audio (opcional).
        """
        segmented_files, path_to_save = self.segment_audio(file_name, index_file, interval, path_to_save)


        # Verificar que todos los archivos estén dentro del tamaño máximo
        while not self._check_all_file_sizes(segmented_files):
            for file_path in segmented_files:
                while not self._check_file_size(file_path):
                    # Reducir el intervalo y segmentar nuevamente
                    interval = interval / 2

                    # Vuelve a segmentar el archivo específico
                    new_file_name = os.path.basename(file_path)
                    new_file_index = segmented_files.index(file_path)
                    path_to_save = os.path.dirname(path_to_save)

                    new_segmented_files = self.segment_audio(file_name=new_file_name, index_file=new_file_index, interval=interval, path_to_save=path_to_save)

                    # Eliminar archivo de segmento anterior
                    os.remove(file_path)

                    # Actualizar la lista de archivos segmentados
                    segmented_files[new_file_index] = new_segmented_files[new_file_index]
                    file_path = segmented_files[new_file_index]
        return segmented_files, path_to_save
    
    def audio_transcribe(self, path:str)->str:
        """
        Transcribe un archivo de audio utilizando la API de OpenAI.

        Args:
            path (str): Ruta del archivo de audio a transcribir.

        Returns:
            str: Texto transcrito del archivo de audio.
        """
        openai.api_key = self.openai_key
        audio_file= open(path, "rb")
        api_response = openai.Audio.transcribe("whisper-1", audio_file)
        response_data = api_response['text']
        decoded_text = unescape(response_data)
        return decoded_text
    
    def multiple_audio_transcription(self, files:List[str])->str:
        """
        Transcribe múltiples archivos de audio utilizando la API de OpenAI y una vez transcrito el audio se elimina el archivo de audio transcrito.

        Args:
            files (List[str]): Lista de archivos de audio a transcribir.

        Returns:
            str: Texto transcrito de los archivos de audio sin la cadena de texto específica.
        """
        full_text = ''
        for file in files:
            if self._check_file_size(file) == False:
                raise Exception(f'{file} size is too big')
            else:
                full_text += self.audio_transcribe(file)
                os.remove(file)
                path_to_full_text = os.path.dirname(file)
                text_file_name = os.path.basename(os.path.dirname(file))
        cadena_a_eliminar = "Subtítulos realizados por la comunidad de Amara.org"
        full_text = full_text.replace(cadena_a_eliminar, '')
        with open(os.path.join(path_to_full_text,f'{text_file_name}.txt'), 'w', encoding='utf-8') as f:
            f.write(full_text)
        return full_text



if __name__ == '__main__':
    transcriber = SpeechToText('C:\\program\\Proyectos_personales\\Reconocimiento_de_audio\\video_samples')
    #transcriber.extract_audio_from_video(file_name= '2023-04-26 17-31-48.mkv')
    # transcriber.print_files_and_index()
    segmented_files, _ = transcriber.segment_audio(index_file=1)
    transcriber.multiple_audio_transcription(segmented_files)