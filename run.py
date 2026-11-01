import argparse,json,sys
from pathlib import Path
from src.agent import Agent
p=argparse.ArgumentParser();p.add_argument('mode',choices=['chat','batch','inspect','validate']);p.add_argument('--dataset',default='./dataset');p.add_argument('--audio-dir');p.add_argument('--output-dir',default='./outputs');a=p.parse_args()
if a.mode=='validate':
    d=Path(a.dataset)
    for folder,n in [('data',7),('kb',21),('practice',2)]:
        files=list((d/folder).glob('*.csv' if folder!='kb' else '*.md'))
        print(folder,len(files),'files', 'OK' if len(files)==n else 'CHECK')
    sys.exit(0)
agent=Agent(a.dataset)
if a.mode=='inspect':print('Indexed',len(agent.sections),'knowledge sections');print(agent.retrieve('refund policy',3))
elif a.mode=='chat':
    print('ZentroMart AI support. Type /quit to exit.')
    while True:
        q=input('Customer > ')
        if q.strip()=='/quit':break
        try: print('Agent >',agent.respond(q)['reply'])
        except Exception as e:print('Error:',e)
elif a.mode=='batch':
    if not a.audio_dir:p.error('--audio-dir is required for batch')
    from src.voice import voice_turn
    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    for file in sorted(Path(a.audio_dir).iterdir()):
        if file.suffix.lower() not in {'.wav','.mp3','.m4a','.ogg'}:continue
        try:
            result=voice_turn(file,Agent(a.dataset),out/(file.stem+'_reply.wav'))
            (out/(file.stem+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
            print('Processed:',file.name)
        except Exception as e:print('FAILED:',file.name,str(e))
