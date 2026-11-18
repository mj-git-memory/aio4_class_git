const form = document.querySelector('#calculator');
const submit = document.querySelector('#submit');
const error = document.querySelector('#error');
const status = document.querySelector('#status');
const operations = {addition: '+', subtraction: '−', multiplication: '×', division: '÷'};
let requestVersion = 0;

// 입력이 바뀌면 이전 결과를 지워서 새 입력의 결과로 오해하지 않도록 한다.
function clearResults() {
  for (const [key, symbol] of Object.entries(operations)) {
    document.getElementById(key).textContent = '—';
    document.getElementById(key).classList.remove('warning');
    document.getElementById(`${key}-expression`).textContent = `첫 번째 숫자 ${symbol} 두 번째 숫자`;
  }
  error.hidden = true;
  status.textContent = '입력을 기다리고 있어요';
}

form.addEventListener('input', () => {
  requestVersion++;
  clearResults();
  submit.disabled = false;
});
form.addEventListener('reset', () => {
  requestVersion++;
  clearResults();
  submit.disabled = false;
  document.querySelector('#a').focus();
});
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const version = ++requestVersion;
  clearResults();
  const a = form.elements.a.value.trim();
  const b = form.elements.b.value.trim();
  const numeric = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/;
  if (!numeric.test(a) || !numeric.test(b)) {
    error.textContent = '두 칸에 숫자를 입력해 주세요. 예: 12.5, -3 (쉼표 없이 입력)';
    error.hidden = false;
    return;
  }
  submit.disabled = true;
  status.textContent = '계산하고 있어요…';
  try {
    // 숫자 문자열 그대로 전송하여 소수의 정확도를 유지한다.
    const response = await fetch('/api/calculate', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({a, b})
    });
    if (version !== requestVersion) return;
    if (!response.ok) {
      throw new Error(response.status === 422
        ? '숫자는 전체 30자리, 소수점 아래 10자리 이내로 입력해 주세요.'
        : '계산에 실패했어요. 잠시 후 다시 시도해 주세요.');
    }
    const result = await response.json();
    if (version !== requestVersion) return;
    for (const [key, symbol] of Object.entries(operations)) {
      document.getElementById(`${key}-expression`).textContent = `(${result.a}) ${symbol} (${result.b})`;
      const output = document.getElementById(key);
      const warning = key === 'division' && result.division_error;
      output.textContent = warning || result[key];
      output.classList.toggle('warning', Boolean(warning));
    }
    status.textContent = '계산이 완료됐어요';
  } catch (failure) {
    if (version !== requestVersion) return;
    error.textContent = failure instanceof TypeError ? '서버에 연결할 수 없어요. 서버 실행 상태를 확인해 주세요.' : failure.message;
    error.hidden = false;
    status.textContent = '입력을 확인해 주세요';
  } finally {
    if (version === requestVersion) submit.disabled = false;
  }
});
