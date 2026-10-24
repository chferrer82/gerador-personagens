// Extrai as constantes de dados do HTML original do artifact (uso único).
// Uso: node extrair.js original.html saida.json
const fs=require('fs'),vm=require('vm');
const [,,src,out]=process.argv;
const L=fs.readFileSync(src,'utf8').split('\n');
const KEYS=['ATR','PATRIA','ASSENT','REG_EXTRA','ANTEC','RACAS','FMT','EXO','IDADE_EXO','RACA_SUP','CLASSES','CLASSE_SUP','SUBCL','DEUSES','IDADE','PB_CUSTO','ARRAY','FAIXAS','ESCALA','VAGA','DESC','DESC_CL','NOMES','NOMES2','ESTILO_LUGAR','SOB_HUMANO'];
// linhas 147–326 (1-based), sem exoRef (182), o push de RACAS (186) e ETAPAS (259)
const bloco=L.slice(146,326).filter((_,i)=>![182,186,259].includes(147+i)).join('\n');
const D=vm.runInNewContext(bloco+'\n;({'+KEYS.join(',')+'})');
const crLine=L[697];
if(!crLine.startsWith('const CR='))throw new Error('linha do CR mudou');
D.CR=vm.runInNewContext(crLine+'\n;CR');
fs.writeFileSync(out,JSON.stringify(D,null,1));
console.log(Object.keys(D).map(k=>k+':'+JSON.stringify(D[k]).length).join(' '));
