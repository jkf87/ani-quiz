from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from docx import Document
import re

class YouTubeWorksheet:
    def __init__(self, api_key):
        # Gemini API 초기화
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
    def get_video_id(self, url):
        # YouTube URL에서 video ID 추출
        video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
        return video_id.group(1) if video_id else None

    def get_transcript(self, url):
        video_id = self.get_video_id(url)
        if not video_id:
            return None
        try:
            # 사용 가능한 모든 자막 목록을 먼저 확인
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 자동 생성된 자막 포함하여 시도
            transcript = transcript_list.find_transcript(['en', 'ko'])
            return ' '.join([entry['text'] for entry in transcript.fetch()])
        except Exception as e:
            print(f"자막 추출 오류: {e}")
            print(f"비디오 ID: {video_id}")
            return None

    def create_worksheet(self, transcript):
        prompt = f"""
        다음 텍스트를 문장별로 나누고, 각 문장에 대해:
        1. 빈칸 문제 만들기 (중요 단어를 ___로 대체)
        2. 한국어로 번역하기
        
        텍스트: {transcript}
        
        표 형식으로 출력:
        원문장|빈칸 문제|한국어 번역
        """
        
        response = self.model.generate_content(prompt)
        return response.text

    def save_to_docx(self, content, output_file="worksheet.docx"):
        doc = Document()
        doc.add_heading('YouTube 학습 활동지', 0)
        
        # 표 생성 및 내용 추가
        rows = content.strip().split('\n')[2:]  # 헤더 제외
        table = doc.add_table(rows=len(rows)+1, cols=3)
        table.style = 'Table Grid'
        
        # 헤더 추가
        headers = ['원문장', '빈칸 문제', '한국어 번역']
        for i, header in enumerate(headers):
            table.cell(0, i).text = header
            
        # 내용 추가
        for i, row in enumerate(rows):
            cells = row.split('|')
            for j, cell in enumerate(cells):
                table.cell(i+1, j).text = cell.strip()
                
        doc.save(output_file)
        return output_file 