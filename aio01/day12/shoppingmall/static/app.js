const content = document.querySelector('#content');
const dialog = document.querySelector('#auth-dialog');
const authForm = document.querySelector('#auth-form');
let user = null, signup = false, pending = null, category = '전체', toastTimer;
const money = value => Number(value).toLocaleString('ko-KR') + '원';
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

async function api(path, options = {}) {
  const response = await fetch('/api' + path, {
    credentials: 'same-origin', ...options,
    headers: {'Content-Type': 'application/json', 'X-Shop-Request': '1', ...options.headers},
  });
  let data;
  try { data = await response.json(); } catch { throw new Error('서버 응답을 확인할 수 없습니다.'); }
  if (!response.ok) {
    const message = Array.isArray(data.detail)
      ? data.detail.map(e => `${e.loc.at(-1)}: ${e.msg}`).join('\n')
      : data.detail || '요청에 실패했습니다.';
    const error = new Error(message);
    error.status = response.status;
    if (response.status === 401) { user = null; updateAuth(); }
    throw error;
  }
  return data;
}
function toast(message) {
  const box = document.querySelector('#toast');
  box.textContent = message; box.classList.add('visible');
  clearTimeout(toastTimer); toastTimer = setTimeout(() => box.classList.remove('visible'), 4000);
}
function updateAuth() {
  document.querySelector('#auth-button').textContent = user ? '로그아웃' : '로그인';
  document.querySelector('#admin-link').hidden = user?.role !== 'admin';
}
function openAuth(action) {
  pending = action || null;
  document.querySelector('#auth-error').textContent = '';
  if (!dialog.open) dialog.showModal();
}
async function authenticated(action) {
  if (!user) { openAuth(action); return; }
  try { await action(); }
  catch (error) {
    if (error.status === 401) openAuth(action);
    else toast(error.message);
  }
}
function empty(title, description) {
  return `<div class="empty"><h2>${esc(title)}</h2><p>${esc(description)}</p><a href="#products"><button>상품 둘러보기 →</button></a></div>`;
}

async function renderProducts() {
  const products = await api('/products');
  content.innerHTML = `<section class="hero"><div><span class="pill">SMALL THINGS, GOOD DAYS</span>
    <h1>일상의 작은 취향,<br>소소하게 채우세요.</h1><p>매일 쓰는 물건일수록 마음에 드는 것으로.<br>당신의 하루를 위한 작은 발견.</p></div><div class="hero-art" aria-hidden="true">👜 ☕</div></section>
    <div class="section-heading"><div><p class="eyebrow">THE EVERYDAY COLLECTION</p><h2>오늘의 소소한 발견</h2></div><div class="filters">${['전체','리빙','패션','문구'].map(c => `<button class="filter ${category === c ? 'active' : ''}" data-category="${c}">${c}</button>`).join('')}</div></div>
    <section class="grid" aria-label="상품 목록">${products.filter(p => category === '전체' || p.category === category).map(p => `<article class="product">
      <div class="product-art" aria-hidden="true">${esc(p.emoji)}</div><div class="product-info"><div class="category">${esc(p.category)}</div><h3>${esc(p.name)}</h3><p class="description">${esc(p.description)}</p><div class="price">${money(p.price)}</div><p class="stock">${p.stock > 0 ? `남은 수량 ${p.stock}개` : '품절'}</p>
      <div class="purchase"><input aria-label="${esc(p.name)} 수량" type="number" min="1" max="${Math.min(99,p.stock)}" value="1"><button class="outline" data-add="${p.id}" ${p.stock ? '' : 'disabled'}>담기</button><button data-buy="${p.id}" ${p.stock ? '' : 'disabled'}>구매하기</button></div></div></article>`).join('')}</section>`;
  content.querySelectorAll('[data-category]').forEach(button => button.onclick = async () => {
    category = button.dataset.category;
    try { await renderProducts(); } catch (error) { toast(error.message); }
  });
  content.querySelectorAll('[data-add],[data-buy]').forEach(button => button.onclick = () => {
    const quantity = Number(button.parentElement.querySelector('input').value);
    const productId = Number(button.dataset.add || button.dataset.buy);
    if (!Number.isInteger(quantity) || quantity < 1 || quantity > 99) return toast('수량은 1~99 사이의 정수로 입력하세요.');
    // 로그인 전의 화면과 선택 수량을 보존하고 로그인 후 이 동작을 재개
    authenticated(async () => {
      button.disabled = true;
      try {
        await api('/cart', {method:'POST',body:JSON.stringify({product_id:productId,quantity})});
        if (button.dataset.buy) location.hash = 'cart';
        else toast('장바구니에 담았습니다.');
      } finally { button.disabled = false; }
    });
  });
}

async function renderCart() {
  const items = await api('/cart');
  content.innerHTML = `<p class="eyebrow">YOUR LITTLE FINDS</p><h2>장바구니</h2>`;
  if (!items.length) { content.innerHTML += empty('아직 장바구니가 비어 있어요', '마음에 드는 물건을 하나씩 담아보세요.'); return; }
  const total = items.reduce((sum,p) => sum+p.price*p.quantity,0);
  content.innerHTML += `<div class="cart-layout"><section class="panel">${items.map(p => `<div class="cart-row"><div class="cart-emoji">${esc(p.emoji)}</div><div class="cart-detail"><h3>${esc(p.name)}</h3><p>${money(p.price)} × ${p.quantity}개</p><strong>${money(p.price*p.quantity)}</strong></div><button class="outline" data-remove="${p.product_id}">삭제</button></div>`).join('')}</section>
    <section class="panel"><h3>주문 정보</h3><form id="checkout-form"><label>배송지<input name="address" required maxlength="300" autocomplete="street-address" value="${esc(user.address)}" placeholder="배송받을 주소"></label><div class="total"><span>합계</span><span>${money(total)}</span></div><p class="note">현재 장바구니 전체 상품을 결제합니다.<br>모의 결제이며 실제 청구되지 않습니다.<br>최종 가격과 재고는 결제 시 다시 확인합니다.</p><button class="wide">모의 결제하기</button></form></section></div>`;
  content.querySelectorAll('[data-remove]').forEach(button => button.onclick = () => authenticated(async () => {
    await api('/cart/'+button.dataset.remove,{method:'DELETE'}); await renderCart();
  }));
  document.querySelector('#checkout-form').onsubmit = event => {
    event.preventDefault();
    const form = event.currentTarget;
    const address = new FormData(form).get('address').trim();
    if (!address) return toast('배송지를 입력하세요.');
    if (!confirm(`${money(total)} 모의 결제를 진행할까요? 실제 청구는 없습니다.`)) return;
    authenticated(async () => {
      const button = form.querySelector('button'); button.disabled = true;
      try {
        const result = await api('/checkout',{method:'POST',body:JSON.stringify({address})});
        toast(result.message); location.hash='orders';
      } finally { button.disabled = false; }
    });
  };
}

async function renderOrders() {
  const orders = await api('/orders');
  content.innerHTML = `<p class="eyebrow">YOUR COLLECTION</p><h2>구매내역</h2>`;
  if (!orders.length) { content.innerHTML += empty('첫 번째 발견을 기다려요', '모의 결제한 주문이 여기에 표시됩니다.'); return; }
  content.innerHTML += orders.map(order => `<article class="panel"><div class="order-head"><div><h3>주문 #${order.id}</h3><small>${new Date(order.paid_at).toLocaleString('ko-KR')}</small></div><span class="badge">${esc(deliveryLabel(order.fulfillment_status))}</span></div><p class="note">배송지: ${esc(order.shipping_address)}</p>${order.items.map(i => `<div class="order-line"><span>${esc(i.product_name)} <small>× ${i.quantity}</small></span><strong>${money(i.unit_price*i.quantity)}</strong></div>`).join('')}<div class="total"><span>결제 금액</span><span>${money(order.total)}</span></div></article>`).join('');
}

async function renderProfile() {
  user = await api('/me');
  content.innerHTML = `<section class="profile"><p class="eyebrow">MY ACCOUNT</p><h2>내 정보</h2><div class="panel"><p class="muted">${esc(user.email)}</p><form id="profile-form"><label>이름<input name="name" required maxlength="50" value="${esc(user.name)}" placeholder="공백 없이 한글·영문"></label><label>기본 배송지<input name="address" maxlength="300" value="${esc(user.address)}" autocomplete="street-address"></label><button class="wide">변경사항 저장</button></form><button id="delete-account" class="danger wide">회원탈퇴</button><p class="note">탈퇴하면 로그인할 수 없으며 개인정보는 익명화됩니다.<br>주문·결제 기록은 유지됩니다.</p></div></section>`;
  document.querySelector('#profile-form').onsubmit = event => {
    event.preventDefault();
    const form = event.currentTarget;
    authenticated(async () => {
      await api('/me',{method:'PATCH',body:JSON.stringify(Object.fromEntries(new FormData(form)))});
      user = await api('/me'); toast('회원정보가 수정되었습니다.');
    });
  };
  document.querySelector('#delete-account').onclick = () => {
    if (!confirm('회원탈퇴를 진행할까요? 다시 로그인할 수 없습니다.')) return;
    authenticated(async () => {
      await api('/me',{method:'DELETE'}); user=null; updateAuth();
      toast('쇼핑몰 탈퇴가 완료되었습니다. 인증 계정 삭제는 운영자에게 요청하세요.'); location.hash='products';
    });
  };
}

async function route() {
  const page = location.hash.slice(1) || 'products';
  document.querySelectorAll('nav a').forEach(a => {
    if (a.hash === '#'+page) a.setAttribute('aria-current','page');
    else a.removeAttribute('aria-current');
  });
  if (page !== 'products' && !user) {
    content.innerHTML = `<div class="empty"><h2>로그인이 필요해요</h2><p>로그인하면 이 화면으로 돌아옵니다.</p><button id="page-login">로그인하기</button></div>`;
    document.querySelector('#page-login').onclick = () => openAuth(route);
    openAuth(route); return;
  }
  try {
    if (page === 'admin') await renderAdmin();
    else if (page === 'cart') await renderCart();
    else if (page === 'orders') await renderOrders();
    else if (page === 'profile') await renderProfile();
    else await renderProducts();
  } catch (error) {
    if (error.status === 401) { openAuth(route); return; }
    content.innerHTML = `<div class="empty"><h2>화면을 불러오지 못했어요</h2><p>${esc(error.message)}</p><button id="retry">다시 시도</button></div>`;
    document.querySelector('#retry').onclick = route;
  }
}

document.querySelector('#auth-button').onclick = async () => {
  if (!user) return openAuth();
  try { const result = await api('/logout',{method:'POST'}); user=null; updateAuth(); toast(result.message); location.hash='products'; await route(); }
  catch (error) { toast(error.message); }
};
document.querySelector('#close-auth').onclick = () => { pending=null; dialog.close(); };
dialog.addEventListener('cancel', () => { pending=null; });
function setAuthMode(value) {
  signup=value;
  document.querySelector('#signup-name').hidden=!signup;
  document.querySelector('#signup-email-help').hidden=!signup;
  authForm.elements.name.required=signup;
  authForm.elements.password.minLength=signup?8:1;
  authForm.elements.password.autocomplete=signup?'new-password':'current-password';
  document.querySelector('#auth-title').textContent=signup?'소소한 취향의 시작':'다시 만나 반가워요';
  document.querySelector('#auth-submit').textContent=signup?'회원가입':'로그인';
  document.querySelector('#switch-auth').textContent=signup?'이미 회원이신가요? 로그인':'처음이신가요? 회원가입';
  document.querySelector('#auth-error').textContent='';
}
document.querySelector('#switch-auth').onclick = () => setAuthMode(!signup);
authForm.onsubmit = async event => {
  event.preventDefault();
  const button=document.querySelector('#auth-submit'); button.disabled=true;
  const values=Object.fromEntries(new FormData(authForm));
  try {
    if (signup) {
      const result = await api('/signup',{method:'POST',body:JSON.stringify(values)});
      setAuthMode(false); authForm.elements.password.value=''; toast(result.message);
    } else {
      await api('/login',{method:'POST',body:JSON.stringify({email:values.email,password:values.password})});
      user=await api('/me'); updateAuth(); dialog.close(); authForm.elements.password.value='';
      const action=pending; pending=null;
      if (action) await action(); else await route();
    }
  } catch (error) {
    if (dialog.open) document.querySelector('#auth-error').textContent=error.message;
    else toast(error.message);
  } finally { button.disabled=false; }
};
window.addEventListener('hashchange',route);
(async () => {
  try { user=await api('/me'); } catch { user=null; }
  updateAuth(); await route();
})();

function deliveryLabel(status) {
  return {preparing:'배송 준비', shipped:'배송 중', delivered:'배송 완료'}[status] || '배송 준비';
}

async function renderAdmin() {
  // 버튼 표시만으로 권한을 보장하지 않는다. 각 API에서도 관리자 여부를 검사한다.
  user = await api('/me'); updateAuth();
  if (user.role !== 'admin') {
    content.innerHTML = empty('관리자 권한이 필요해요', '이 화면은 운영자만 사용할 수 있습니다.');
    return;
  }
  const [products, orders] = await Promise.all([api('/admin/products'), api('/admin/orders')]);
  const fields = p => `<label>상품명<input name="name" required maxlength="100" value="${esc(p.name)}"></label>
    <label>설명<input name="description" required maxlength="1000" value="${esc(p.description)}"></label>
    <label>카테고리<select name="category">${['리빙','패션','문구'].map(c => `<option ${p.category === c ? 'selected' : ''}>${c}</option>`).join('')}</select></label>
    <label>가격(원)<input name="price" type="number" min="1" max="100000000" required value="${p.price ?? 1000}"></label>
    <label>재고<input name="stock" type="number" min="0" max="1000000" required value="${p.stock ?? 0}"></label>
    <label>그림 문자<input name="emoji" required maxlength="20" value="${esc(p.emoji || '📦')}"></label>
    <label>판매 상태<select name="active"><option value="true" ${p.active !== false ? 'selected' : ''}>판매 중</option><option value="false" ${p.active === false ? 'selected' : ''}>판매 중지</option></select></label>`;
  content.innerHTML = `<p class="eyebrow">STORE MANAGEMENT</p><h2>상품·주문 관리</h2>
    <p class="note">가격·재고 변경은 이후 결제에 적용됩니다. 기존 구매 기록은 유지됩니다.</p>
    <details class="panel"><summary>새 상품 등록</summary><form data-product="new" class="admin-form">${fields({})}<button>등록</button></form></details>
    <h3>상품 ${products.length}개</h3>${products.map(p => `<details class="panel"><summary>${esc(p.emoji)} ${esc(p.name)} · ${money(p.price)} · 재고 ${p.stock} · ${p.active ? '판매 중' : '판매 중지'}</summary><form data-product="${p.id}" class="admin-form">${fields(p)}<button>변경사항 저장</button></form></details>`).join('')}
    <h3>최근 결제 주문 (최대 200건)</h3>${orders.length ? orders.map(o => `<article class="panel"><h3>주문 #${o.id} · ${money(o.total)}</h3><p>${esc(o.customer_name)} · ${esc(o.shipping_address)}</p><p>${esc(deliveryLabel(o.fulfillment_status))}</p>${o.fulfillment_status !== 'delivered' ? `<button data-delivery="${o.id}" data-status="${o.fulfillment_status === 'preparing' ? 'shipped' : 'delivered'}">${o.fulfillment_status === 'preparing' ? '배송 시작' : '배송 완료 처리'}</button>` : ''}</article>`).join('') : '<p>결제 주문이 없습니다.</p>'}`;
  content.querySelectorAll('[data-product]').forEach(form => form.onsubmit = async event => {
    event.preventDefault();
    const button = form.querySelector('button'); button.disabled = true;
    const values = Object.fromEntries(new FormData(form));
    values.price = Number(values.price); values.stock = Number(values.stock); values.active = values.active === 'true';
    const isNew = form.dataset.product === 'new';
    try {
      await api('/admin/products' + (isNew ? '' : '/' + form.dataset.product), {
        method:isNew ? 'POST' : 'PUT', body:JSON.stringify(values),
      });
      toast(isNew ? '상품을 등록했습니다.' : '상품을 수정했습니다.'); await renderAdmin();
    } catch (error) { toast(error.message); }
    finally { button.disabled = false; }
  });
  content.querySelectorAll('[data-delivery]').forEach(button => button.onclick = async () => {
    if (!confirm('주문 #' + button.dataset.delivery + '의 배송 상태를 변경할까요?')) return;
    button.disabled = true;
    try {
      await api('/admin/orders/' + button.dataset.delivery + '/fulfillment', {
        method:'PATCH', body:JSON.stringify({status:button.dataset.status}),
      });
      toast('배송 상태를 변경했습니다.'); await renderAdmin();
    } catch (error) { toast(error.message); }
    finally { button.disabled = false; }
  });
}
