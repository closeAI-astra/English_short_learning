/* Included inside the existing English Express closure. Reuses ICON, store and scheduler. */
ICON.repeat='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M19 8a8 8 0 1 0 1 7M19 3v5h-5M12 7v5l3 2"/></svg>';
ICON.headphones='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 14V11a8 8 0 0 1 16 0v3M10 9v6M14 7v10"/><rect x="3" y="12" width="4" height="8" rx="2"/><rect x="17" y="12" width="4" height="8" rx="2"/></svg>';
const LAB_MODES=[['recall','想起練習','book','隠して、思い出す'],['review','間隔反復','repeat','今日の復習を、少しずつ'],['hvpt','聞き分け','headphones','声が変わっても、聞き取る'],['fluency','4 / 3 / 2','mic','同じ話を、もっと滑らかに']];
const LAB={mode:'recall',topic:'all',id:EE_MICRO[0].id,revealed:false,rated:false,queue:false};
const LP={pack:null,urls:[],cur:null,played:false,answered:false,token:0,audio:null,split:'train',n:0,ok:0,lastVoice:''};
const LF={round:0,durations:[240,180,120],deadline:0,timer:null,pending:false,token:0,rec:null,stream:null,urls:[],results:[],topic:'最近学んだことを、例を挙げて説明する',draft:''};
function labHome(){
  const n=EEStudy.dueLessons(EE_MICRO,S.progress).length;
  return '<div class="lab-hero"><div class="lab-eyebrow">YOUR DAILY PRACTICE</div><h2>知っている英語を、<br>使える英語に。</h2><p>聞いて終わりにしない。思い出す・日を空ける・聞き分ける・話す。今日の自分に合う練習から。</p><div class="lab-grid">'+LAB_MODES.map((m,i)=>'<button class="lab-link" data-go="lab:'+m[0]+'"><span class="lab-num">0'+(i+1)+'</span><span class="lab-icon" aria-hidden="true">'+ICON[m[2]]+'</span><b>'+m[1]+'</b><small>'+(m[0]==='review'?n+'本が復習日です':m[3])+'</small></button>').join('')+'</div></div>';
}
function labSaveLocal(key,value){try{localStorage.setItem(key,JSON.stringify(value));return true;}catch(e){toast('端末への保存に失敗しました。空き容量を確認してください。');return false;}}
function labHistory(kind,value){const key='ee-lab-'+kind;const rows=lsGet(key,[]);labSaveLocal(key,[value,...(Array.isArray(rows)?rows:[])].slice(0,100));}
function labDate(t){return new Date(t).toLocaleString('ja-JP',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'});}
function labEnter(mode){
  LAB.mode=LAB_MODES.some(x=>x[0]===mode)?mode:'recall';
  if(LAB.mode!=='hvpt')labStopListening();
  $('#labTabs').innerHTML=LAB_MODES.map(m=>'<button data-labmode="'+m[0]+'" aria-pressed="'+(LAB.mode===m[0])+'">'+m[1]+'</button>').join('');
  if(LAB.mode==='recall')labRecall();
  if(LAB.mode==='review')labReview();
  if(LAB.mode==='hvpt')labPerception();
  if(LAB.mode==='fluency')labFluency();
}
$('#labTabs').onclick=e=>{const b=e.target.closest('[data-labmode]');if(b){labLeave();labEnter(b.dataset.labmode);}};
function labLeave(){labStopListening();if(LF.deadline)labFinish(true);if(LF.pending){LF.token++;LF.pending=false;}stopSpeech();}
function labRecall(){
  const list=EE_MICRO.filter(x=>LAB.topic==='all'||x.topic===LAB.topic);
  const item=list.find(x=>x.id===LAB.id)||list[0];LAB.id=item.id;LAB.revealed=false;LAB.rated=false;
  const topics=[...new Set(EE_MICRO.map(x=>x.topic))];
  $('#labBody').innerHTML='<div class="card stack"><div class="grid2"><label class="field">分野<select id="labTopic"><option value="all">すべての分野</option>'+topics.map(t=>'<option>'+esc(t)+'</option>').join('')+'</select></label><label class="field">教材<select id="labLesson">'+list.map(x=>'<option value="'+x.id+'">'+esc(x.title)+'</option>').join('')+'</select></label></div><div class="lab-meta"><span>'+esc(item.topic)+'</span><span>オリジナル短文</span><span>想起 → 確認 → 復習</span></div><h2>'+esc(item.title)+'</h2><p class="lab-copy">'+esc(item.japanese)+'</p><p class="small ink2">この場面を英語で説明してみましょう。全文の暗唱でなく、自分の言葉でも構いません。</p><textarea id="labRecallText" aria-label="思い出した英語" placeholder="まず声に出すか、ここに書いてみる（メモは保存しません）"></textarea><div class="row"><button class="btn" id="labHint">音声のヒント</button><button class="btn primary" id="labReveal">英文を確認する</button></div><div id="labAnswer" class="lab-answer stack" hidden><div class="lab-copy">'+esc(item.english)+'</div><div>使い回せる表現：<b>'+esc(item.phrase)+'</b></div><div class="row"><button class="btn" id="labListen">手本を聞く</button><button class="btn" id="labPron">発音練習へ</button></div></div><div id="labRating" hidden><p class="small" style="margin-bottom:10px">答えを見る前、どこまで思い出せましたか？</p><div class="lab-rate">'+[[1,'思い出せない'],[2,'ヒントがあれば'],[3,'自力で言えた']].map(([g,l])=>'<button class="btn" data-labrate="'+g+'">'+l+'<small>次は '+fmtIvl(schedule(S.progress[item.id],g).due-Date.now())+'後</small></button>').join('')+'</div></div><div id="labSaved" role="status" class="small"></div><div class="row"><button class="btn" id="labNext">次の教材</button><button class="btn" data-go="lab:review">復習一覧へ</button></div><p class="lab-note">復習日は既存の記憶モデルで計算する目安です。最適日や習得を保証する判定ではありません。</p></div>';
  $('#labTopic').value=LAB.topic;$('#labLesson').value=item.id;
  $('#labTopic').onchange=e=>{LAB.topic=e.target.value;LAB.queue=false;labRecall();};
  $('#labLesson').onchange=e=>{LAB.id=e.target.value;LAB.queue=false;labRecall();};
  $('#labHint').onclick=()=>{speak(item.english);$('#labHint').textContent='ヒントを聞きました';};
  $('#labReveal').onclick=()=>{LAB.revealed=true;$('#labAnswer').hidden=false;$('#labRating').hidden=false;$('#labReveal').disabled=true;};
  $('#labListen').onclick=()=>speak(item.english);
  $('#labPron').onclick=()=>{const a=document.createElement('a');a.href=coachURL(item.english);a.target='_blank';a.rel='noopener';a.click();};
  $$('[data-labrate]').forEach(b=>b.onclick=()=>{
    if(!LAB.revealed||LAB.rated)return;LAB.rated=true;
    const p=schedule(S.progress[item.id],+b.dataset.labrate);put('progress',item.id,p);bump({reviews:1});
    $$('[data-labrate]').forEach(x=>x.disabled=true);$('#labSaved').textContent='保存しました。次の復習：'+labDate(p.due);
  });
  $('#labNext').onclick=()=>{stopSpeech();if(LAB.queue){const due=EEStudy.dueLessons(EE_MICRO,S.progress).filter(x=>x.id!==LAB.id);if(!due.length){labEnter('review');return;}LAB.id=due[0].id;}else LAB.id=list[(list.findIndex(x=>x.id===LAB.id)+1)%list.length].id;labRecall();};
}
function labReview(){
  const due=EEStudy.dueLessons(EE_MICRO,S.progress), later=EE_MICRO.filter(x=>S.progress[x.id]&&S.progress[x.id].due>Date.now()).sort((a,b)=>S.progress[a.id].due-S.progress[b.id].due);
  $('#labBody').innerHTML='<div class="card stack"><div class="lab-eyebrow">SPACED PRACTICE</div><h2>今日の復習 '+due.length+'本</h2><p class="ink2">新しい教材を増やす前に、前回の内容を思い出す時間を。</p><div class="row"><button class="btn primary" id="labDue" '+(!due.length?'disabled':'')+'>期限が来た教材から始める</button><button class="btn" data-go="words">フレーズの復習 '+wordCounts().due+'枚</button></div>'+(due.length?'':'<p>いま期限が来ている短文はありません。想起練習で自己評価すると、次の復習日が入ります。</p>')+[...due,...later].slice(0,30).map(x=>'<div class="lab-queue"><div><b>'+esc(x.title)+'</b><small>'+esc(x.topic)+' ・ '+labDate(S.progress[x.id].due)+'</small></div><button class="btn sm" data-labopen="'+x.id+'">'+(S.progress[x.id].due<=Date.now()?'復習する':'先に練習する')+'</button></div>').join('')+'<p class="lab-note">期限はアプリを開いたときに確認します。バックグラウンド通知は送りません。端末の保存領域を消すと、ローカルの記録は消えます。</p></div>';
  $('#labDue').onclick=()=>{LAB.topic='all';LAB.id=due[0].id;LAB.queue=true;labEnter('recall');};
  $$('[data-labopen]').forEach(b=>b.onclick=()=>{LAB.topic='all';LAB.id=b.dataset.labopen;LAB.queue=false;labEnter('recall');});
}
function labStopListening(){LP.token++;LP.played=false;if(LP.audio){LP.audio.pause();LP.audio=null;}stopSpeech();}
function labPerception(){
  const results=lsGet('ee-lab-perception',[]);
  $('#labBody').innerHTML='<div class="card stack"><div class="lab-eyebrow">LISTEN TO THE DIFFERENCE</div><h2>声が変わっても、聞き分ける。</h2><p class="ink2">2つの単語のどちらが聞こえたか選びます。答えを見て、もう一度聞き直しましょう。</p><label class="field">音声と練習の種類<select id="labAudioMode"><option value="tts">合成音声で練習（HVPTの補助）</option><option value="train" '+(!LP.pack?'disabled':'')+'>自然話者の録音で練習</option><option value="test" '+(!LP.pack?.test.length?'disabled':'')+'>未練習の話者・単語で確認</option></select></label><p id="labVoice" class="lab-note" role="status"></p><div class="row"><button class="btn primary" id="labHear">音声を聞く</button><button class="btn" id="labHPNext">次の問題</button></div><div class="pairbtns" id="labHPAnswers"></div><div id="labHPFeedback" role="status"></div><div class="lab-note" id="labHPScore">このセット：'+LP.ok+' / '+LP.n+'問正解</div><details><summary>自然話者の音声教材を読み込む</summary><div class="body stack"><p class="small">manifest.json と、その中で指定した音声をまとめて選択。録音は外部送信せず、このタブでのみ使います。利用権のある複数の自然話者の録音を用意してください。</p><input id="labPack" type="file" multiple accept=".json,.wav,.mp3,.ogg,.m4a,.webm" aria-label="音声教材ファイル"><p class="lab-note">練習は2人以上。確認用は練習と異なる話者・単語が必要です。詳しい形式は同梱の HVPT_PACK.md を参照。</p><div id="labPackStatus" role="status"></div></div></details><p class="lab-note">合成音声の声数は端末に依存します。合成音声だけでは自然話者を用いたHVPT研究と同じ条件になりません。</p><details><summary>最近の練習記録（この端末）</summary><div class="body">'+results.slice(0,8).map(r=>'<p class="small">'+labDate(r.at)+' ・ '+esc(r.source)+' ・ '+(r.ok?'正解':'復習')+'</p>').join('')+'</div></details></div>';
  $('#labAudioMode').onchange=()=>{LP.n=0;LP.ok=0;labHPNext();};
  $('#labPack').onchange=async e=>{
    try{const files=[...e.target.files], manifests=files.filter(f=>f.name==='manifest.json');if(manifests.length!==1)throw Error('manifest.json を1つ選んでください。');if(manifests[0].size>1024*1024)throw Error('manifest.json は1MB以下にしてください。');
      const pack=EEStudy.validatePack(JSON.parse(await manifests[0].text()),files.filter(f=>f!==manifests[0]));
      labStopListening();LP.urls.forEach(URL.revokeObjectURL);LP.urls=[];
      pack.samples.forEach(s=>{s.url=URL.createObjectURL(files.find(f=>f.name===s.file));LP.urls.push(s.url);});LP.pack=pack;LP.n=0;LP.ok=0;labPerception();$('#labAudioMode').value='train';labHPNext();$('#labPackStatus').textContent=pack.speakerCount+'人の練習音声を読み込みました。';
    }catch(err){$('#labPackStatus').textContent=err.message;}
  };
  $('#labHear').onclick=labHPPlay;$('#labHPNext').onclick=labHPNext;labHPNext();
}
function labHPNext(){
  labStopListening();LP.answered=false;const mode=$('#labAudioMode').value;LP.split=mode;
  if(mode==='tts'){
    const c=pickContrast(), pair=rand(c.pairs), available=voices.filter(v=>/^en[-_]/i.test(v.lang));
    const different=available.filter(v=>v.name!==LP.lastVoice), voice=rand(different.length?different:available);LP.lastVoice=voice?.name||'';
    LP.cur={pair,answer:Math.random()<.5?0:1,voice};
    $('#labVoice').textContent=available.length+'種類の英語合成音声を検出。'+(available.length<2?'この端末では話者の変化が不足します。':'問題ごとに声を切り替えます。');
  }else{const pool=LP.pack?.[mode]||[];if(!pool.length){$('#labVoice').textContent='対応する音声教材を読み込んでください。';return;}LP.cur=rand(pool);$('#labVoice').textContent=mode==='test'?'未練習の話者・単語を使う確認モード':'自然話者の録音を使う練習モード';}
  $('#labHPAnswers').innerHTML=LP.cur.pair.map((w,i)=>'<button disabled data-hpanswer="'+i+'">'+esc(w)+'</button>').join('');$('#labHPFeedback').textContent='先に音声を聞いてください。';$('#labHPScore').textContent='このセット：'+LP.ok+' / '+LP.n+'問正解';
  $$('[data-hpanswer]').forEach(b=>b.onclick=()=>{
    if(!LP.played||LP.answered)return;LP.answered=true;const ok=+b.dataset.hpanswer===LP.cur.answer;LP.n++;if(ok)LP.ok++;
    $$('[data-hpanswer]').forEach(x=>{x.disabled=true;if(+x.dataset.hpanswer===LP.cur.answer)x.classList.add('right');else if(x===b)x.classList.add('wrong');});
    $('#labHPFeedback').textContent=(ok?'正解。':'今回は違いました。')+' 聞こえた単語：'+LP.cur.pair[LP.cur.answer]+'。同じ音声をもう一度聞けます。';
    $('#labHPScore').textContent='このセット：'+LP.ok+' / '+LP.n+'問正解';labHistory('perception',{at:Date.now(),source:LP.split==='tts'?'合成音声':LP.split==='test'?'自然音声・確認':'自然音声・練習',ok});
  });
}
async function labHPPlay(){
  const c=LP.cur;if(!c)return;const token=++LP.token;LP.played=false;$$('[data-hpanswer]').forEach(b=>b.disabled=true);
  try{
    if(LP.audio)LP.audio.pause();
    if(LP.split==='tts'){
      if(!('speechSynthesis' in window))throw Error('この端末では読み上げを使えません。');
      speechSynthesis.cancel();
      await new Promise((resolve,reject)=>{const u=new SpeechSynthesisUtterance(c.pair[c.answer]);if(c.voice)u.voice=c.voice;u.lang=c.voice?.lang||'en-US';u.rate=1;
        const timeout=setTimeout(()=>{speechSynthesis.cancel();reject(Error('音声の再生を確認できませんでした。もう一度試してください。'));},15000);
        u.onend=()=>{clearTimeout(timeout);resolve();};u.onerror=()=>{clearTimeout(timeout);reject(Error('音声を再生できませんでした。'));};speechSynthesis.speak(u);
      });
    }
    else{LP.audio=new Audio(c.url);await LP.audio.play();}
    if(token!==LP.token)return;LP.played=true;if(!LP.answered){$$('[data-hpanswer]').forEach(b=>b.disabled=false);$('#labHPFeedback').textContent='どちらが聞こえましたか？';}
  }catch(e){if(token===LP.token)$('#labHPFeedback').textContent=e.message;}
}
function labFluency(){
  const saved=lsGet('ee-lab-fluency-draft',null);if(!LF.results.length&&!LF.draft&&saved){LF.topic=saved.topic||LF.topic;LF.draft=saved.text||'';}
  $('#labBody').innerHTML='<div class="card stack"><div class="lab-eyebrow">ONE STORY. THREE ROUNDS.</div><h2>同じ話を、少しずつ滑らかに。</h2><label class="field">3回とも同じテーマ<input id="labFTopic" value="'+esc(LF.topic)+'" '+(LF.round?'disabled':'')+'></label><div class="lab-rounds">'+LF.durations.map((d,i)=>'<span class="'+(LF.round===i?'active':'')+'">ROUND '+(i+1)+' · '+d/60+'分</span>').join('')+'</div><div id="labFTimer" class="lab-timer">'+fmtSec(LF.durations[LF.round]||0)+'</div><label class="chk"><input type="checkbox" id="labFRecord">マイクで録音する（任意・外部送信しません）</label><div class="row"><button class="btn primary" id="labFStart" '+(LF.round>=3?'disabled':'')+'>今回のスピーチを始める</button><button class="btn" id="labFStop" disabled>ここで終える</button><button class="btn" id="labFReset">新しい3ラウンド</button></div><textarea id="labFDraft" placeholder="話した内容・振り返りメモ（この端末に保存）" aria-label="スピーチメモ">'+esc(LF.draft)+'</textarea><label class="chk"><input type="checkbox" id="labFMeaning">伝えたかった内容を保てた</label><div id="labFStatus" role="status" class="small"></div><div id="labFResults" class="stack"></div><p class="lab-note">タイマーは実際の経過時間で動きます。画面を離れるとその回を中断して保存し、同じ回をやり直せます。録音はこのタブの間だけ保持します。必要なら保存してください。語数はメモの値で、音声を自動採点しません。</p><details><summary>以前のスピーチ記録</summary><div class="body">'+lsGet('ee-lab-fluency',[]).slice(0,6).map(r=>'<div class="lab-queue"><div>'+esc(r.topic)+'<small>'+labDate(r.at)+' ・ '+Math.round(r.sec)+'秒 ・ '+(r.interrupted?'中断':r.early?'早期終了':'完了')+'</small></div></div>').join('')+'</div></details></div>';
  $('#labFStart').onclick=labFStart;$('#labFStop').onclick=()=>labFinish(false);$('#labFReset').onclick=()=>{if(LF.pending){LF.token++;LF.pending=false;}if(LF.deadline)labFinish(true);LF.urls.forEach(URL.revokeObjectURL);LF.urls=[];LF.results=[];LF.round=0;LF.draft='';labSaveLocal('ee-lab-fluency-draft',{topic:LF.topic,text:''});labFluency();};
  $('#labFDraft').oninput=e=>{LF.draft=e.target.value;labSaveLocal('ee-lab-fluency-draft',{topic:LF.topic,text:LF.draft});};
  $('#labFTopic').onchange=e=>{LF.topic=e.target.value;labSaveLocal('ee-lab-fluency-draft',{topic:LF.topic,text:LF.draft});};labFResults();
}
async function labFStart(){
  if(LF.pending||LF.deadline||LF.round>=3)return;const token=++LF.token;LF.pending=true;$('#labFStart').disabled=true;
  try{
    LF.topic=$('#labFTopic').value.trim();if(!LF.topic)throw Error('話すテーマを入力してください。');
    LF.rec=null;
    if($('#labFRecord').checked){if(!navigator.mediaDevices?.getUserMedia||!window.MediaRecorder)throw Error('このブラウザーでは録音できません。録音なしで練習できます。');
      const stream=await navigator.mediaDevices.getUserMedia({audio:true});if(token!==LF.token){stream.getTracks().forEach(t=>t.stop());return;}LF.stream=stream;
      const parts=[],rec=new MediaRecorder(stream);LF.rec=rec;rec.ondataavailable=e=>{if(e.data.size)parts.push(e.data);};
      rec.onstop=()=>{stream.getTracks().forEach(t=>t.stop());if(rec.result&&parts.length){const url=URL.createObjectURL(new Blob(parts,{type:rec.mimeType}));rec.result.url=url;rec.result.mime=rec.mimeType;LF.urls.push(url);if((LAB.mode==='fluency'&&curTab==='lab')||(curTab==='watch'&&V.mode==='fluency'))labFResults();}};rec.start();
    }
    LF.pending=false;LF.draft='';$('#labFDraft').value='';$('#labFMeaning').checked=false;$('#labFTopic').disabled=true;$('#labFRecord').disabled=true;$('#labFStop').disabled=false;
    LF.started=Date.now();LF.deadline=LF.started+LF.durations[LF.round]*1000;$('#labFStatus').textContent='同じ内容を落ち着いて伝えましょう。';
    LF.timer=setInterval(()=>{const left=EEStudy.remaining(LF.deadline);if($('#labFTimer'))$('#labFTimer').textContent=fmtSec(left);if(!left)labFinish(false);},200);
  }catch(e){LF.stream?.getTracks().forEach(t=>t.stop());LF.stream=null;LF.pending=false;if($('#labFStart')){$('#labFStart').disabled=false;$('#labFStatus').textContent='録音を始められませんでした：'+e.message;}}
}
function labFinish(interrupted){
  if(!LF.deadline)return;clearInterval(LF.timer);const duration=LF.durations[LF.round],sec=Math.min(duration,(Date.now()-LF.started)/1000);
  const r={at:Date.now(),round:LF.round+1,topic:LF.topic,sec,text:$('#labFDraft')?.value||LF.draft,meaning:!!$('#labFMeaning')?.checked,interrupted,early:sec<duration-1};
  LF.results.push(r);labHistory('fluency',r);LF.deadline=0;LF.draft=r.text;
  if(LF.rec?.state==='recording'){LF.rec.result=r;LF.rec.stop();}LF.stream?.getTracks().forEach(t=>t.stop());LF.stream=null;
  if(!interrupted)LF.round++;if($('#labFStart')){$('#labFStart').disabled=LF.round>=3;$('#labFStop').disabled=true;$('#labFRecord').disabled=false;$('#labFTimer').textContent=fmtSec(LF.durations[LF.round]||0);$('#labFStatus').textContent=interrupted?'中断した回を記録しました。同じ回から再開できます。':LF.round>=3?'3回終了。速さだけでなく、伝えたい内容を保てたか振り返りましょう。':'今回の記録を保存しました。次も同じ話をします。';$$('.lab-rounds span').forEach((x,i)=>x.classList.toggle('active',i===LF.round));labFResults();}
}
function labFResults(){const box=$('#labFResults');if(!box)return;box.innerHTML=LF.results.map((r,i)=>'<div class="lab-answer"><b>'+r.round+'回目 · '+Math.round(r.sec)+'秒'+(r.interrupted?'（中断）':r.early?'（早期終了）':'')+'</b><p class="small">'+(r.meaning?'内容を保てた':'内容の保持：未確認')+' ・ メモ '+countWords(r.text)+'語</p>'+(r.url?'<audio controls src="'+r.url+'"></audio><a download="speech-round-'+r.round+(r.mime?.includes('mp4')?'.m4a':r.mime?.includes('ogg')?'.ogg':'.webm')+'" href="'+r.url+'">録音を保存</a>':'')+'</div>').join('');}
window.addEventListener('pagehide',()=>{if(LF.deadline)labFinish(true);labStopListening();LF.stream?.getTracks().forEach(t=>t.stop());});
