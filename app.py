from youtube_worksheet import YouTubeWorksheet
from dotenv import load_dotenv
import gradio as gr
import os

def process_video(url):
    # 환경변수에서 API 키 가져오기
    API_KEY = os.getenv('GEMINI_API_KEY')
    
    if not API_KEY:
        return "ERROR: GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요."
    
    worksheet = YouTubeWorksheet(API_KEY)
    
    # 자막 추출
    transcript = worksheet.get_transcript(url)
    if not transcript:
        return "자막을 추출할 수 없습니다."
    
    # 워크시트 생성
    content = worksheet.create_worksheet(transcript)
    
    # DOCX 파일로 저장
    output_file = worksheet.save_to_docx(content)
    
    return f"워크시트가 생성되었습니다. 파일명: {output_file}", output_file

def main():
    # Gradio 인터페이스 실행
    iface = gr.Interface(
        fn=process_video,
        inputs=[gr.Textbox(label="YouTube URL을 입력하세요")],
        outputs=[gr.Textbox(label="처리 결과"), gr.File(label="생성된 워크시트")],
        title="YouTube 학습 워크시트 생성기",
        description="YouTube 영상의 자막을 이용하여 학습 워크시트를 생성합니다."
    )
    iface.launch(share=True)

if __name__ == '__main__':
    load_dotenv()
    main() 