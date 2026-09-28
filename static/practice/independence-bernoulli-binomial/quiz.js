import { questions } from './questions.mjs';

const $ = (id) => document.getElementById(id);
const escape = (value) => String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
const blank = () => ({ choice: null, result: null, hint: false });
let answers = questions.map(blank);
let current = 0;
const notes = '/files/independence-bernoulli-binomial-2026-09-28.pdf';
const status = (answer) => answer.result === true ? 'Correct' : answer.result === false ? 'Revisit' : 'Unchecked';

function updateProgress() {
  const checked = answers.filter((answer) => answer.result !== null).length;
  const correct = answers.filter((answer) => answer.result === true).length;
  $('counts').textContent = `${checked}/${questions.length} checked · ${correct} correct`;
  $('progress').value = checked;
  $('progress').max = questions.length;
  $('question-nav').innerHTML = questions.map((q, i) => {
    const answer = answers[i];
    const symbol = answer.result === true ? '✓' : answer.result === false ? '↻' : '·';
    const color = answer.result === true ? 'correct' : answer.result === false ? 'incorrect' : '';
    return `<button type="button" class="question-number ${color}" data-question="${i}" ${current === i ? 'aria-current="step"' : ''} aria-label="Question ${i + 1}: ${escape(q.topic)}. ${status(answer)}">${i + 1}<span class="mark" aria-hidden="true">${symbol}</span></button>`;
  }).join('');
}

function showQuestion(index, focus = true) {
  current = index;
  const q = questions[index];
  const answer = answers[index];
  const checked = answer.result !== null;
  $('summary-panel').hidden = true;
  $('question-panel').hidden = false;
  $('question-panel').innerHTML = `
    <p class="topic">${index + 1} / ${questions.length} · ${escape(q.topic)}</p>
    <h2 id="question-heading" tabindex="-1">${escape(q.prompt)}</h2>
    <form id="answer-form" novalidate>
      <fieldset ${checked ? 'disabled' : ''}>
        <legend>Choose one answer.</legend>
        <div class="options">${q.choices.map((choice, i) => `<label class="option ${checked && i === q.answer ? 'correct-answer' : checked && i === answer.choice ? 'wrong-answer' : ''}"><input type="radio" name="answer" value="${i}" ${answer.choice === i ? 'checked' : ''}><span>${escape(choice)}</span></label>`).join('')}</div>
      </fieldset>
      <p id="validation" class="validation" role="status"></p>
      <details id="hint" ${answer.hint ? 'open' : ''}><summary>Need a hint?</summary><p>${escape(q.hint)}</p></details>
      <div class="actions">${checked ? '<button id="retry" type="button">Try this question again</button>' : '<button class="primary" type="submit">Check answer</button>'}</div>
    </form>
    <div id="feedback" ${checked ? '' : 'hidden'} class="feedback ${answer.result ? 'correct' : ''}" tabindex="-1" role="region" aria-label="Answer feedback">
      ${checked ? `<h3>${answer.result ? 'Correct.' : 'Not quite. Let’s work through it.'}</h3><p><strong>Answer: ${escape(q.choices[q.answer])}</strong></p><p>${escape(q.explanation)}</p>` : ''}
    </div>
    <p class="notes-link"><a href="${notes}#page=${q.page}" target="_blank" rel="noopener">Review notes, pages ${q.pages} <span class="small">(opens PDF in a new tab)</span></a></p>
    <div class="question-footer"><button id="previous" type="button" ${index === 0 ? 'disabled' : ''}>← Previous</button><button id="next" type="button">${index === questions.length - 1 ? 'Review progress →' : 'Next →'}</button></div>`;
  $('answer-form').addEventListener('change', (event) => {
    if (event.target.name === 'answer') { answer.choice = Number(event.target.value); $('validation').textContent = ''; }
  });
  $('hint').addEventListener('toggle', (event) => { answer.hint = event.target.open; });
  $('answer-form').addEventListener('submit', (event) => {
    event.preventDefault();
    if (answer.result !== null) return;
    if (answer.choice === null) { $('validation').textContent = 'Choose an answer before checking.'; return; }
    answer.result = answer.choice === q.answer;
    showQuestion(index, false);
    $('feedback').focus();
  });
  $('retry')?.addEventListener('click', () => { answers[index] = blank(); showQuestion(index); });
  $('previous').addEventListener('click', () => showQuestion(index - 1));
  $('next').addEventListener('click', () => index < questions.length - 1 ? showQuestion(index + 1) : showSummary());
  updateProgress();
  if (focus) $('question-heading').focus();
}

function showSummary() {
  current = -1;
  $('question-panel').hidden = true;
  $('summary-panel').hidden = false;
  const correct = answers.filter((answer) => answer.result === true).length;
  const checked = answers.filter((answer) => answer.result !== null).length;
  $('summary-panel').innerHTML = `
    <p class="topic">Pause &amp; reflect</p>
    <h2 id="summary-heading" tabindex="-1">${correct === questions.length ? 'All twelve correct. Keep the reasoning.' : 'Your practice so far.'}</h2>
    <p><strong>${correct} of ${questions.length} correct</strong> · ${checked} checked</p>
    <p class="small">Counts reflect your latest check of each question. Retries replace that question’s result. Reloading clears this practice session.</p>
    <p>${correct === questions.length ? 'Try explaining why expectations always add, when variances add, and why the two cereal errors use different distributions.' : 'Return to any question below. Use the linked notes when you want to revisit the derivation.'}</p>
    <ol class="results">${questions.map((q, i) => `<li><button type="button" data-question="${i}">${i + 1}. ${escape(q.topic)}</button><span class="result-status">${status(answers[i])}</span></li>`).join('')}</ol>
    <div class="actions">${correct < questions.length ? '<button id="retry-missed" class="primary" type="button">Reset missed answers</button>' : ''}<button id="restart" type="button">Start over</button></div>
    <div id="reset-confirmation" class="notice" hidden><p>Clear all answers and begin again?</p><div class="actions"><button id="confirm-reset" type="button">Yes, clear answers</button><button id="cancel-reset" type="button">Keep my progress</button></div></div>`;
  $('retry-missed')?.addEventListener('click', () => {
    answers = answers.map((answer) => answer.result === true ? answer : blank());
    showQuestion(answers.findIndex((answer) => answer.result !== true));
  });
  $('restart').addEventListener('click', () => { $('reset-confirmation').hidden = false; $('cancel-reset').focus(); });
  $('cancel-reset').addEventListener('click', () => { $('reset-confirmation').hidden = true; $('restart').focus(); });
  $('confirm-reset').addEventListener('click', () => { answers = questions.map(blank); showQuestion(0); });
  updateProgress();
  $('summary-heading').focus();
}

$('practice').addEventListener('click', (event) => {
  const button = event.target.closest('button[data-question]');
  if (button) showQuestion(Number(button.dataset.question));
});
$('review').addEventListener('click', showSummary);
$('loading').hidden = true;
$('practice').hidden = false;
showQuestion(0, false);
