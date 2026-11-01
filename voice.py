import os
from gnani.stt import GnaniSTTClient
from gnani.tts import GnaniTTSClient
def voice_turn(audio_path,agent,output_path):
    if not os.getenv('GNANI_API_KEY'):raise RuntimeError('GNANI_API_KEY is required')
    language=os.getenv('GNANI_LANGUAGE','en-IN')
    result=GnaniSTTClient().transcribe(str(audio_path),language_code=language)
    transcript=result.get('transcript','')
    response=agent.respond(transcript) if transcript.strip() else {'reply':'Sorry, I did not catch that. Please repeat.','sources':[]}
    GnaniTTSClient().synthesize(response['reply'],voice='Kaveri',model='timbre-v2.5',language=language,output_file=str(output_path))
    return {'transcript':transcript,**response,'audio':str(output_path)}
