'use strict';
const $ = (id) => document.getElementById(id);
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
function message(text, error = false) {
  const box = $('app-message');
  box.textContent = text;
  box.classList.toggle('error', error);
  box.hidden = false;
  box.focus();
}
async function api(path, method = 'GET', data) {
  const response = await fetch(path, {
    method, credentials: 'same-origin', cache: 'no-store',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
    ...(data === undefined ? {} : { body: JSON.stringify(data) }),
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(result.error || '요청을 처리하지 못했습니다. 새로고침 후 다시 시도해 주세요.');
  return result;
}
function node(tag, text, className) {
  const el = document.createElement(tag);
  if (text !== undefined) el.textContent = text;
  if (className) el.className = className;
  return el;
}
function timestamp(value) {
  return new Date(value).toLocaleString('ko-KR', { dateStyle: 'medium', timeStyle: 'short' });
}
function handle(action) {
  return async (event) => {
    event.preventDefault();
    const button = event.submitter || event.currentTarget;
    if (button.disabled) return;
    button.disabled = true;
    try { await action(event); } catch (error) { message(error.message, true); }
    finally { button.disabled = false; }
  };
}

if ($('guestbook')) {
  let page = Number($('guestbook').dataset.page);
  let pages = Number($('page-label').textContent.split('/')[1]);
  let selected = null;
  let detailVersion = 0;
  let listVersion = 0;
  let lastTrigger = null;

  function closeDetail(restoreFocus = true) {
    detailVersion += 1;
    selected = null;
    $('post-detail').hidden = true;
    $('edit-form').hidden = true;
    $('edit-body').value = '';
    $('delete-confirm').hidden = true;
    document.querySelectorAll('[data-post-id]').forEach(el => el.setAttribute('aria-expanded', 'false'));
    if (restoreFocus && lastTrigger?.isConnected) lastTrigger.focus();
  }

  async function refreshList(target = page) {
    const version = ++listVersion;
    const data = await api(`/api/posts?page=${target}`);
    if (version !== listVersion) return;
    page = data.page;
    pages = data.pages;
    $('post-count').textContent = data.total;
    $('page-label').textContent = `${page} / ${pages}`;
    $('prev-page').disabled = page <= 1;
    $('next-page').disabled = page >= pages;
    $('empty-state').hidden = data.total > 0;
    $('post-list').replaceChildren(...data.posts.map(post => {
      const li = node('li');
      const button = node('button', undefined, 'post-row');
      button.type = 'button';
      button.dataset.postId = post.id;
      button.setAttribute('aria-controls', 'post-detail');
      button.setAttribute('aria-expanded', String(post.id === selected));
      const icon = node('span', '↗', 'note-icon');
      icon.setAttribute('aria-hidden', 'true');
      const main = node('span', undefined, 'row-main');
      main.append(node('span', post.preview, 'preview'), node('span', `${post.nickname} · ${timestamp(post.created_at)}`, 'row-meta'));
      const arrow = node('span', '→', 'row-arrow');
      arrow.setAttribute('aria-hidden', 'true');
      button.append(icon, main, arrow);
      li.append(button);
      return li;
    }));
    history.replaceState(null, '', page === 1 ? '/' : `/?page=${page}`);
  }

  async function openDetail(id, focus = true) {
    const version = ++detailVersion;
    selected = id;
    const data = await api(`/api/posts/${id}`);
    if (version !== detailVersion) return;
    $('detail-meta').textContent = `${data.nickname} · ${timestamp(data.created_at)}`;
    $('detail-body').textContent = data.body;
    $('owner-actions').hidden = !data.is_owner;
    $('edit-form').hidden = true;
    $('edit-body').value = '';
    $('delete-confirm').hidden = true;
    $('comment-count').textContent = data.comments.length;
    $('comment-list').replaceChildren(...data.comments.map(comment => {
      const li = node('li');
      li.append(node('small', `${comment.nickname} · ${timestamp(comment.created_at)}`), node('p', comment.body));
      return li;
    }));
    $('no-comments').hidden = data.comments.length > 0;
    $('post-detail').hidden = false;
    document.querySelectorAll('[data-post-id]').forEach(el => el.setAttribute('aria-expanded', String(el.dataset.postId === id)));
    if (focus) $('post-detail').focus();
  }

  $('post-list').addEventListener('click', async event => {
    const button = event.target.closest('[data-post-id]');
    if (!button) return;
    const id = button.dataset.postId;
    lastTrigger = button;
    // Do not keep a previous post visible while another request is in flight.
    closeDetail(false);
    try { await openDetail(id); }
    catch (error) {
      if (selected === id) { closeDetail(false); message(error.message, true); }
    }
  });
  $('close-detail').addEventListener('click', () => closeDetail());
  async function changePage(target) {
    closeDetail(false);
    $('prev-page').disabled = true;
    $('next-page').disabled = true;
    try { await refreshList(target); }
    catch (error) { message(error.message, true); }
    finally {
      $('prev-page').disabled = page <= 1;
      $('next-page').disabled = page >= pages;
    }
  }
  $('prev-page').addEventListener('click', () => changePage(page - 1));
  $('next-page').addEventListener('click', () => changePage(page + 1));

  $('post-form')?.addEventListener('submit', handle(async () => {
    if (!$('post-body').value.trim()) throw new Error('본문을 입력해 주세요.');
    const data = await api('/api/posts', 'POST', { body: $('post-body').value });
    $('post-form').reset();
    await refreshList(1);
    await openDetail(data.id);
    message('새로운 기록을 남겼습니다.');
  }));
  $('edit-post').addEventListener('click', handle(async () => {
    const id = selected;
    const data = await api(`/api/posts/${id}/edit`);
    if (selected !== id) return;
    $('edit-body').value = data.body;
    $('edit-form').hidden = false;
    $('delete-confirm').hidden = true;
    $('edit-body').focus();
  }));
  $('cancel-edit').addEventListener('click', () => { $('edit-form').hidden = true; $('edit-body').value = ''; });
  $('edit-form').addEventListener('submit', handle(async () => {
    const id = selected;
    if (!$('edit-body').value.trim()) throw new Error('본문을 입력해 주세요.');
    await api(`/api/posts/${id}`, 'PATCH', { body: $('edit-body').value });
    await refreshList();
    if (selected === id) await openDetail(id, false);
    message('기록을 수정했습니다.');
  }));
  $('ask-delete').addEventListener('click', () => { $('delete-confirm').hidden = false; $('confirm-delete').focus(); });
  $('cancel-delete').addEventListener('click', () => { $('delete-confirm').hidden = true; });
  $('confirm-delete').addEventListener('click', handle(async () => {
    const id = selected;
    await api(`/api/posts/${id}`, 'DELETE');
    if (selected === id) closeDetail(false);
    await refreshList();
    message('기록과 연결된 댓글을 삭제했습니다.');
  }));
  $('comment-form')?.addEventListener('submit', handle(async () => {
    const id = selected;
    if (!$('comment-body').value.trim()) throw new Error('댓글을 입력해 주세요.');
    await api(`/api/posts/${id}/comments`, 'POST', { body: $('comment-body').value });
    $('comment-form').reset();
    if (selected === id) await openDetail(id, false);
    message('댓글을 남겼습니다.');
  }));
  window.addEventListener('pageshow', event => {
    if (event.persisted) {
      const id = selected;
      refreshList().then(() => id && openDetail(id, false)).catch(error => message(error.message, true));
    }
  });
}

$('rule-form')?.addEventListener('submit', handle(async () => {
  await api('/api/rules', 'POST', {
    type: $('rule-type').value, pattern: $('rule-pattern').value, flags: $('rule-flags').value,
  });
  window.location.reload();
}));
document.querySelectorAll('.rule-delete').forEach(button => button.addEventListener('click', () => {
  button.hidden = true;
  button.parentElement.querySelector('.rule-confirm').hidden = false;
}));
document.querySelectorAll('.rule-delete-cancel').forEach(button => button.addEventListener('click', () => {
  button.closest('.rule-confirm').hidden = true;
  button.closest('.rule-delete-actions').querySelector('.rule-delete').hidden = false;
}));
document.querySelectorAll('.rule-delete-confirm').forEach(button => button.addEventListener('click', handle(async () => {
  await api(`/api/rules/${button.dataset.ruleId}`, 'DELETE');
  window.location.reload();
})));
