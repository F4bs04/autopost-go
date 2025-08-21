// Configuração da API - detecta automaticamente se está em produção ou desenvolvimento
const API_BASE = window.location.origin;

const input = document.getElementById('tema');
const btn = document.getElementById('btnEnviar');
const estiloImagem = document.getElementById('estiloImagem');
const statusEl = document.getElementById('status');
const loader = document.getElementById('loader');
const resultado = document.getElementById('resultado');
const imgTema = document.getElementById('imgTema');
const titulo = document.getElementById('titulo');
const subtitulo = document.getElementById('subtitulo');
const conteudo = document.getElementById('conteudo');
const fontes = document.getElementById('fontes');
const btnRegerarTexto = document.getElementById('btnRegerarTexto');
const btnRegerarImagem = document.getElementById('btnRegerarImagem');

function escapeHTML(str) {
  return (str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function mapImageErrorMessage(err) {
  const e = (err || '').toLowerCase();
  if (e.includes('insufficient_quota') || e.includes('quota') || e.includes('credit')) {
    return 'Não foi possível gerar a imagem: sua conta pode estar sem créditos de API.';
  }
  if (e.includes('organization must be verified') || e.includes('verified to use the model')) {
    return 'Não foi possível gerar a imagem: a organização precisa estar verificada para usar o modelo de imagens.';
  }
  if (e.includes('invalid value') && e.includes('size')) {
    return 'Não foi possível gerar a imagem: tamanho de imagem inválido para o modelo. Tente novamente mais tarde.';
  }
  if (e.includes('api key') || e.includes('authentication')) {
    return 'Não foi possível gerar a imagem: verifique sua OPENAI_API_KEY.';
  }
  return 'Não foi possível gerar a imagem. Verifique a chave OPENAI_API_KEY, créditos e permissões do modelo.';
}

function formatTextToHTML(text) {
  const safe = escapeHTML(text || '');
  // Split by double newlines into paragraphs
  const paragraphs = safe.split(/\n\n+/).map(p => p.trim()).filter(Boolean);
  if (paragraphs.length === 0) return '';
  return paragraphs
    .map(p => `<p>${p.replace(/\n/g, '<br/>')}</p>`) // single \n -> <br/>
    .join('');
}

function setLoading(loading, msg = '') {
  btn.disabled = loading;
  input.disabled = loading;
  estiloImagem.disabled = loading;
  statusEl.textContent = msg;
  if (loader) {
    if (loading) loader.classList.add('show');
    else loader.classList.remove('show');
  }
}

// Função para tratar erros de rede e API
function handleFetchError(error, context = 'operação') {
  console.error(`Erro na ${context}:`, error);
  
  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    return `Erro de conexão: Verifique se a aplicação está rodando corretamente. ${error.message}`;
  }
  
  if (error.message.includes('500')) {
    return `Erro interno do servidor: Verifique se a chave OPENAI_API_KEY está configurada corretamente.`;
  }
  
  if (error.message.includes('404')) {
    return `Endpoint não encontrado: Verifique se a API está rodando na URL correta.`;
  }
  
  if (error.message.includes('CORS')) {
    return `Erro de CORS: Problema de configuração entre frontend e backend.`;
  }
  
  return `Erro na ${context}: ${error.message}`;
}

async function gerar() {
  const tema = (input.value || '').trim();
  const estilo = estiloImagem.value || 'realista';
  if (!tema) {
    statusEl.textContent = 'Digite um tema para gerar conteúdo';
    input.focus();
    return;
  }

  setLoading(true, 'Gerando conteúdo e imagem... isso pode levar alguns segundos');
  resultado.classList.add('hidden');

  try {
    const resp = await fetch(`${API_BASE}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tema, estilo_imagem: estilo })
    });

    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(`Erro ${resp.status}: ${text}`);
    }

    const data = await resp.json();
    const content = data.conteudo || {};

    const newTitle = content.titulo || '';
    const newSubtitle = content.subtitulo || '';
    titulo.textContent = newTitle || 'Sem título';
    subtitulo.textContent = newSubtitle || '';
    // toggle visibility
    titulo.style.display = newTitle ? '' : 'none';
    subtitulo.style.display = newSubtitle ? '' : 'none';
    conteudo.innerHTML = formatTextToHTML(content.conteudo || '');

    // fontes
    fontes.innerHTML = '';
    (content.fontes || []).forEach(f => {
      const div = document.createElement('div');
      div.className = 'fonte';
      div.innerHTML = `
        <div><strong>${f.titulo || ''}</strong></div>
        <div><a href="${f.link || '#'}" target="_blank" rel="noopener">${f.link || ''}</a></div>
        <div>${f.resumo || ''}</div>
      `;
      fontes.appendChild(div);
    });

    // imagem
    const img = content.imagem || {};
    const publicUrl = img.public_url || img.local_path || '';
    if (publicUrl) {
      imgTema.src = publicUrl;
      imgTema.alt = content.titulo || 'Imagem do tema';
    } else {
      imgTema.removeAttribute('src');
      imgTema.alt = 'Imagem não disponível';
    }

    // informar erro de imagem, se o backend reportou
    if (content.imagem_error) {
      const friendly = mapImageErrorMessage(content.imagem_error);
      statusEl.textContent = friendly;
    }

    resultado.classList.remove('hidden');
    setLoading(false, 'Concluído!');
  } catch (err) {
    const errorMsg = handleFetchError(err, 'geração de conteúdo');
    setLoading(false, errorMsg);
  }
}

btn.addEventListener('click', gerar);
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') gerar();
});

async function regerarTexto() {
  const tema = (input.value || '').trim();
  if (!tema) {
    statusEl.textContent = 'Digite um tema para regerar o texto';
    input.focus();
    return;
  }
  setLoading(true, 'Regerando texto...');
  try {
    const resp = await fetch(`${API_BASE}/api/regenerate-text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tema })
    });
    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(`Erro ${resp.status}: ${text}`);
    }
    const data = await resp.json();
    const content = data.conteudo || {};
    const rtTitle = content.titulo || '';
    const rtSubtitle = content.subtitulo || '';
    titulo.textContent = rtTitle || 'Sem título';
    subtitulo.textContent = rtSubtitle || '';
    titulo.style.display = rtTitle ? '' : 'none';
    subtitulo.style.display = rtSubtitle ? '' : 'none';
    conteudo.innerHTML = formatTextToHTML(content.conteudo || '');
    // não altera imagem
    // fontes
    fontes.innerHTML = '';
    (content.fontes || []).forEach(f => {
      const div = document.createElement('div');
      div.className = 'fonte';
      div.innerHTML = `
        <div><strong>${f.titulo || ''}</strong></div>
        <div><a href="${f.link || '#'}" target="_blank" rel="noopener">${f.link || ''}</a></div>
        <div>${f.resumo || ''}</div>
      `;
      fontes.appendChild(div);
    });
    resultado.classList.remove('hidden');
    setLoading(false, 'Texto atualizado!');
  } catch (err) {
    const errorMsg = handleFetchError(err, 'regeneração de texto');
    setLoading(false, errorMsg);
  }
}

async function regerarImagem() {
  // usa o titulo atual como prompt principal, e o tema do input como elemento
  const tituloAtual = (titulo.textContent || '').trim();
  const tema = (input.value || '').trim();
  const estilo = estiloImagem.value || 'realista';
  if (!tituloAtual) {
    statusEl.textContent = 'Gere conteúdo primeiro para obter um título';
    return;
  }
  setLoading(true, 'Regerando imagem...');
  try {
    const resp = await fetch(`${API_BASE}/api/regenerate-image`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ titulo: tituloAtual, tema: tema || null, estilo_imagem: estilo })
    });
    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(`Erro ${resp.status}: ${text}`);
    }
    const data = await resp.json();
    if (data && data.error) {
      // erro detalhado do backend
      imgTema.removeAttribute('src');
      imgTema.alt = 'Imagem não disponível';
      statusEl.textContent = mapImageErrorMessage(data.error);
      throw new Error(data.error);
    }
    const image = (data && data.imagem) || {};
    const publicUrl = image.public_url || image.local_path || '';
    if (publicUrl) {
      imgTema.src = publicUrl;
      imgTema.alt = tituloAtual || 'Imagem do tema';
    } else {
      imgTema.removeAttribute('src');
      imgTema.alt = 'Imagem não disponível';
    }
    resultado.classList.remove('hidden');
    setLoading(false, 'Imagem atualizada!');
  } catch (err) {
    const errorMsg = handleFetchError(err, 'regeneração de imagem');
    setLoading(false, errorMsg);
  }
}

if (btnRegerarTexto) btnRegerarTexto.addEventListener('click', regerarTexto);
if (btnRegerarImagem) btnRegerarImagem.addEventListener('click', regerarImagem);
