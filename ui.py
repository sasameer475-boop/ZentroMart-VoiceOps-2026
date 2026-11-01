import gradio as gr
from src.agent import Agent
from src.voice import voice_turn
from pathlib import Path
agent=Agent()
def answer(text):
    try:return agent.respond(text)['reply']
    except Exception as e:return f'Error: {e}'
def speak(audio):
    if not audio:return 'Upload or record a clip first.',None
    try:
        Path('outputs').mkdir(exist_ok=True)
        r=voice_turn(audio,agent,'outputs/reply.wav')
        return 'Heard: '+r['transcript']+'\n\nReply: '+r['reply'],r['audio']
    except Exception as e:return f'Voice error: {e}',None
with gr.Blocks(title='ZentroMart VoiceOps') as demo:
    gr.Markdown('# ZentroMart AI Customer Support')
    with gr.Tab('Text'):
        q=gr.Textbox(label='Customer question');response=gr.Textbox(label='Agent response');gr.Button('Ask').click(answer,q,response)
    with gr.Tab('Voice'):
        audio=gr.Audio(sources=['microphone','upload'],type='filepath',label='Customer audio');out=gr.Textbox(label='Transcript and answer');voice=gr.Audio(label='Spoken reply');gr.Button('Process voice').click(speak,audio,[out,voice])
if __name__=='__main__':demo.launch()
