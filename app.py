from youtube_worksheet import YouTubeWorksheet
from dotenv import load_dotenv
import gradio as gr
import os
import asyncio
from pathlib import Path
import time

# 임시 파일 저장을 위한 디렉토리 설정
UPLOAD_DIR = Path("temp_files")
UPLOAD_DIR.mkdir(exist_ok=True)

async def process_video(url):
    try:
        # 환경변수에서 API 키 가져오기
        API_KEY = os.getenv('GEMINI_API_KEY')
        
        if not API_KEY:
            return "ERROR: GEMINI_API_KEY가 설정되지 않았습니다.", None
        
        worksheet = YouTubeWorksheet(API_KEY)
        
        # 자막 추출 (타임아웃 설정)
        try:
            transcript = await asyncio.wait_for(
                asyncio.to_thread(worksheet.get_transcript, url),
                timeout=30
            )
        except asyncio.TimeoutError:
            return "자막 추출 시간이 초과되었습니다.", None
        except Exception as e:
            return f"자막 추출 중 오류 발생: {str(e)}", None
            
        if not transcript:
            return "자막을 추출할 수 없습니다. 영상에 영�� 또는 한국어 자막이 있는지 확인해주세요.", None
        
        # 워크시트 생성
        try:
            content = await asyncio.wait_for(
                asyncio.to_thread(worksheet.create_worksheet, transcript),
                timeout=60
            )
        except asyncio.TimeoutError:
            return "워크시트 생성 시간이 초과되었습니다.", None
        except Exception as e:
            return f"워크시트 생성 중 오류 발생: {str(e)}", None
        
        # 임시 파일명 생성
        temp_file = UPLOAD_DIR / f"worksheet_{os.urandom(8).hex()}.docx"
        
        # DOCX 파일로 저장
        try:
            await asyncio.to_thread(worksheet.save_to_docx, content, str(temp_file))
        except Exception as e:
            return f"파일 저장 중 오류 발생: {str(e)}", None
        
        return "워크시트가 생성되었습니다.", str(temp_file)
        
    except Exception as e:
        return f"처리 중 예상치 못한 오류가 발생했습니다: {str(e)}", None

def clean_temp_files():
    """30분 이상 된 임시 파일들을 삭제"""
    current_time = time.time()
    for file in UPLOAD_DIR.glob("*.docx"):
        if current_time - file.stat().st_mtime > 1800:  # 30분
            try:
                file.unlink()
            except:
                pass

def main():
    # 환경 변수 로드
    load_dotenv()
    
    # 주기적으로 임시 파일 정리
    clean_temp_files()
    
    # Gradio 인터페이스 설정
    iface = gr.Interface(
        fn=process_video,
        inputs=[
            gr.Textbox(
                label="YouTube URL을 입력하세요",
                placeholder="https://www.youtube.com/watch?v=..."
            )
        ],
        outputs=[
            gr.Textbox(label="처리 결과"),
            gr.File(label="생성된 워크시트")
        ],
        title="YouTube 학습 워크시트 생성기",
        description="YouTube 영상의 자막을 이용하여 학습 워크시트를 생성합니다.",
        allow_flagging="never",
        examples=[["https://www.youtube.com/watch?v=example"]]
    )
    
    # Render의 환경 변수에서 PORT 가져오기
    port = int(os.environ.get("PORT", 7860))
    
    # 서버 시작
    iface.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,  # Render에서는 share 옵션 비활성화
        auth=None,    # 필요한 경우 인증 추가
        ssl_verify=False  # SSL 검증 비활성화
    )

if __name__ == '__main__':
    main()
