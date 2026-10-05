#!/usr/bin/env python3
"""Exercise the white paper's local coordination example in disposable storage.

Run: python docs/media/verify_white_paper_example.py --output /path/to/result.json
This fixture simulates role handoffs; it starts no subagents or external jobs.
"""
import sys
if __name__ == '__main__' and not sys.flags.isolated:
    _bootstrap_os = sys.modules.get('os')
    if _bootstrap_os is None or not sys.executable:
        sys.exit('White-paper example verifier requires Python isolated mode')
    try:
        _bootstrap_os.execv(sys.executable, [sys.executable, '-I', '-B', __file__, *sys.argv[1:]])
    except OSError as error:
        sys.exit('White-paper example verifier could not enter isolated mode: ' + str(error))

from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import secrets
import stat
import subprocess
import tempfile

REPO = Path(__file__).resolve().parents[2]

def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_output(path, content):
    if os.name != 'posix' or not all(hasattr(os,name) for name in ('O_DIRECTORY','O_NOFOLLOW')):
        raise RuntimeError('Safe example output requires POSIX directory-descriptor operations')
    directory_fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    temporary_name=None
    try:
        try:
            existing=os.stat(path.name,dir_fd=directory_fd,follow_symlinks=False)
        except FileNotFoundError:
            existing=None
        if existing is not None and not stat.S_ISREG(existing.st_mode):
            raise ValueError('Example output must be a regular file')
        candidate_name='.systemx-example-'+secrets.token_hex(16)+'.json'
        flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW
        temporary_fd=os.open(candidate_name,flags,0o600,dir_fd=directory_fd)
        temporary_name=candidate_name
        with os.fdopen(temporary_fd,'w',encoding='utf-8') as draft:
            draft.write(content)
        try:
            current=os.stat(path.name,dir_fd=directory_fd,follow_symlinks=False)
        except FileNotFoundError:
            current=None
        if current is not None and not stat.S_ISREG(current.st_mode):
            raise ValueError('Example output changed to a non-regular file')
        os.replace(temporary_name,path.name,src_dir_fd=directory_fd,dst_dir_fd=directory_fd)
        temporary_name=None
    finally:
        if temporary_name is not None:
            os.unlink(temporary_name,dir_fd=directory_fd)
        os.close(directory_fd)

def run_example():
    commands = []
    def command(args, expected=0):
        result = subprocess.run([str(x) for x in args], capture_output=True, text=True)
        if (expected == 0 and result.returncode != 0) or (expected != 0 and result.returncode == 0):
            raise AssertionError(result.stderr or result.stdout)
        commands.append({'operation': str(args[-1]) if len(args) < 5 else str(args[3]),
                         'returncode': result.returncode})
        return result.stdout
    with tempfile.TemporaryDirectory(prefix='systemx-white-paper-') as temp:
        target = Path(temp)/'Example Project'
        command([sys.executable, '-I', '-B', REPO/'.SYSTEMX/manager.py', 'install',
                 '--source', REPO/'.SYSTEMX', '--target', target])
        root = target/'.SYSTEMX'
        launcher = [sys.executable, '-I', '-B', root/'manager.py', 'run', '--target', target, '--offline', '--']
        def cli(*args, expected=0):
            return command(launcher + list(args), expected)
        def jcli(*args):
            return json.loads(cli(*args))
        cli('agent-add', 'agent.1', '--role', 'implementer')
        jcli('roles-init', '--apply')
        cli('task-add', '--owner', 'agent.1', '--title', 'Create a local status page',
            '--scope', 'index.html', '--acceptance', 'Title is Status',
            '--acceptance', 'Level-one heading is Status', '--acceptance', 'UTF-8 declaration is present')
        ledger_before = (root/'WORK/TASKS.json').read_bytes()
        cli('task-set', 'TASK-001', '--status', 'done', '--reviewer', 'agent.0',
            '--evidence', 'not-a-real-result', expected=1)
        assert (root/'WORK/TASKS.json').read_bytes() == ledger_before
        cli('focus', '--objective', 'Verify the local status page', '--task', 'TASK-001')
        cli('task-set', 'TASK-001', '--status', 'in_progress', '--next', 'Create and check index.html')
        packet = cli('task-packet', 'TASK-001', '--base', 'empty-local-fixture')
        assert 'does not dispatch a worker' in packet
        evidence = target/'evidence'; evidence.mkdir()
        page = target/'index.html'
        page.write_text('<!doctype html><meta charset="utf-8"><title>Status</title>\n', encoding='utf-8')
        check = target/'check.py'
        check.write_text('''from pathlib import Path
import json,sys
text=Path(__file__).with_name('index.html').read_text(encoding='utf-8')
checks={'title':'<title>Status</title>' in text,'heading':'<h1>Status</h1>' in text,'utf8':'charset="utf-8"' in text}
print(json.dumps({'checks':checks,'passed':all(checks.values())},sort_keys=True))
sys.exit(0 if all(checks.values()) else 1)
''', encoding='utf-8')
        failed = command([sys.executable, '-I', '-B', check], expected=1)
        (evidence/'check-fail.json').write_text(failed)
        failed_revision = digest(page.read_bytes())
        at = datetime.now(timezone.utc).isoformat()
        event_args = ['agent-x', 'event', '--key', 'local-check-failed-001', '--at', at,
                      '--actor-kind', 'automation', '--actor-id', 'local-check', '--kind', 'check',
                      '--stage', 'failed', '--revision', failed_revision,
                      '--summary', 'Heading criterion failed', '--task', 'TASK-001',
                      '--evidence', 'evidence/check-fail.json']
        event = jcli(*event_args)
        replay = jcli(*event_args)
        assert replay['created'] is False and replay['event'] == event['event']
        events_before = (root/'EVENTS/EVENTS.json').read_bytes()
        conflict = event_args.copy(); conflict[conflict.index('--summary')+1] = 'Different facts'
        cli(*conflict, expected=1)
        assert (root/'EVENTS/EVENTS.json').read_bytes() == events_before
        page.write_text(page.read_text()+'<h1>Status</h1>\n', encoding='utf-8')
        passed = command([sys.executable, '-I', '-B', check]); (evidence/'check-pass.json').write_text(passed)
        revision = digest(page.read_bytes()); evidence_revision = digest(passed.encode())
        jcli('agent-x','event','--key','local-check-passed-002','--at',datetime.now(timezone.utc).isoformat(),
             '--actor-kind','automation','--actor-id','local-check','--kind','check','--stage','checked',
             '--revision',revision,'--summary','All three local criteria passed','--task','TASK-001',
             '--evidence','evidence/check-pass.json')
        cli('task-set','TASK-001','--status','needs_review','--evidence','evidence/check-pass.json')
        prepared=jcli('agent-z','prepare','--kind','task','--subject','TASK-001','--task','TASK-001',
                      '--revision',revision,'--evidence-revision',evidence_revision,'--stage','checked','--apply')
        request_id=prepared['request']['id']
        first=jcli('agent-z','score',request_id,'--apply')
        assert first['report']['score']['points']==0
        request_file=root/prepared['requestPath']; request=json.loads(request_file.read_text())
        for answer in request['answers'][:2]:
            answer.update(result='pass', note='The task states its local outcome and three explicit acceptance criteria.',
                          evidence=['WORK/TASKS.json#TASK-001'])
        request_file.write_text(json.dumps(request,indent=2)+'\n',encoding='utf-8')
        second=jcli('agent-z','score',request_id,'--apply')
        repeated=jcli('agent-z','score',request_id,'--apply')
        assert repeated['reused'] and repeated['report']==second['report']
        assert second['report']['score']['points']==2 and second['report']['score']['counts']['unknown']==98
        comparison=jcli('agent-z','compare',first['report']['id'],second['report']['id'])
        assert comparison['pointDelta']==2 and comparison['automaticWork'] is False
        jcli('agent-z','validate',second['report']['id'])
        command([sys.executable,'-I','-B',check])  # Coordinator checks accepted local artifact.
        cli('task-set','TASK-001','--status','done','--reviewer','agent.0',
            '--evidence','evidence/check-pass.json','--note','Three local HTML criteria verified')
        checkpoint=root/'MEMORY/sessions/local-example.md'
        checkpoint.write_text('# Local example\n\nTASK-001 accepted against three local HTML criteria.\n'
                              'Evidence: evidence/check-fail.json and evidence/check-pass.json.\n'
                              'No browser, hosting or live-service verification was performed.\n'
                              'Next action: hand off the accepted local result; no further task authorized.\n',encoding='utf-8')
        cli('focus','--objective','Accepted local status page','--task','TASK-001',
            '--checkpoint','MEMORY/sessions/local-example.md')
        due_at=datetime.now(timezone.utc).isoformat()
        schedule=jcli('agent-x','schedule','--key','local-follow-up-001','--title','Review local acceptance',
                      '--due',due_at,'--owner','user','--task','TASK-001')
        assert schedule['jobCreated'] is False
        due=jcli('agent-x','due','--as-of',due_at)
        assert schedule['item']['id'] in json.dumps(due)
        jcli('agent-x','close',schedule['item']['id'],'--state','complete',
             '--note','Local acceptance reviewed','--evidence','evidence/check-pass.json')
        cli('validate')
        task=json.loads((root/'WORK/TASKS.json').read_text())['tasks'][0]
        assert task['status']=='done' and task['reviewedBy']=='agent.0'
        assert [h['status'] for h in task['history']]==['todo','in_progress','needs_review','done']
        assert 'TASK-001' in (root/'WORK/DONE.md').read_text()
        assert 'local-example.md' in (root/'CURRENT.md').read_text()
        return {'passed':True,'scope':'Disposable local HTML coordination fixture',
                'recordedAt':datetime.now(timezone.utc).isoformat(),
                'templateVersion':(REPO/'.SYSTEMX/VERSION').read_text().strip(),
                'checks':{'initialCheckFailed':True,'correctedCheckPassed':True,
                          'invalidTransitionPreservedLedger':True,'eventReplayReused':True,
                          'conflictingReplayPreservedLedger':True,'scoreReplayReused':True,
                          'reviewPointDelta':2,'unknownAnswersRetained':98,
                          'taskStates':[h['status'] for h in task['history']],
                          'generatedViewsValidated':True,'externalJobCreated':False},
                'artifactSha256':revision,'checkEvidenceSha256':evidence_revision,
                'commandCount':len(commands),'temporaryProjectRemoved':True,
                'limits':'No subagent process, browser, deployment or live service was tested. This is not a complete 100-answer judgment or production review.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(); result=run_example()
    encoded=json.dumps(result,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        output=args.output.parent.resolve()/args.output.name
        write_output(output,encoded)
    print(encoded,end='')
