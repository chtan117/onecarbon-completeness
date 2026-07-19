(function () {
  let currentSector = null;
  let items = [];        // {id, name, scope, group, optional}
  let answers = {};       // id -> "Present" | "Absent" | "Unsure"
  let showingOptional = false;

  const screenSector = document.getElementById('screen-sector');
  const screenCheck = document.getElementById('screen-check');
  const screenSummary = document.getElementById('screen-summary');
  const sectorGrid = document.getElementById('sector-grid');
  const groupContainer = document.getElementById('group-container');
  const checkTitle = document.getElementById('check-title');
  const progressFill = document.getElementById('progress-fill');
  const progressLabel = document.getElementById('progress-label');

  function setStep(n) {
    for (let i = 1; i <= 3; i++) {
      const dot = document.getElementById('step-dot-' + i);
      dot.classList.remove('active', 'done');
      if (i < n) dot.classList.add('done');
      if (i === n) dot.classList.add('active');
    }
  }

  // ---- Step 1: sector picker ----
  Object.keys(SECTORS).forEach(function (name) {
    const required = SECTORS[name].filter(function (s) { return !s.optional; }).length;
    const btn = document.createElement('button');
    btn.className = 'sector-card';
    btn.innerHTML = name + '<span class="count">' + required + ' sources to check</span>';
    btn.onclick = function () { startSector(name); };
    sectorGrid.appendChild(btn);
  });

  function startSector(name) {
    currentSector = name;
    items = SECTORS[name].filter(function (s) { return !s.optional; });
    showingOptional = false;
    answers = {};
    items.forEach(function (s) { answers[s.id] = null; });

    checkTitle.textContent = name + ' \u2014 mark what applies';
    screenSector.style.display = 'none';
    screenCheck.style.display = 'block';
    screenSummary.style.display = 'none';
    setStep(2);
    renderChecklist();
  }

  function renderChecklist() {
    groupContainer.innerHTML = '';
    const groups = ['Your operations', 'Your energy', 'Your value chain'];
    groups.forEach(function (groupName) {
      const groupItems = items.filter(function (s) { return s.group === groupName; });
      if (groupItems.length === 0) return;
      const h = document.createElement('p');
      h.className = 'group-header';
      h.textContent = groupName;
      groupContainer.appendChild(h);
      groupItems.forEach(function (s) { groupContainer.appendChild(sourceRow(s)); });
    });

    const optional = SECTORS[currentSector].filter(function (s) { return s.optional; });
    if (optional.length > 0 && !showingOptional) {
      const more = document.createElement('button');
      more.className = 'show-more-btn';
      more.textContent = 'Show ' + optional.length + ' additional source' + (optional.length > 1 ? 's' : '') + ' for edge cases in this sector';
      more.onclick = function () {
        showingOptional = true;
        optional.forEach(function (s) { if (!(s.id in answers)) answers[s.id] = null; });
        items = items.concat(optional);
        renderChecklist();
      };
      groupContainer.appendChild(more);
    }
    updateProgress();
  }

  function sourceRow(s) {
    const row = document.createElement('div');
    row.className = 'source-row';
    const label = document.createElement('span');
    label.className = 'name';
    label.textContent = s.name;
    const btns = document.createElement('div');
    btns.className = 'answer-btns';
    [['Present', 'sel-present'], ['Absent', 'sel-absent'], ['Unsure', 'sel-unsure']].forEach(function (pair) {
      const opt = pair[0], cls = pair[1];
      const b = document.createElement('button');
      b.className = 'answer-btn';
      b.textContent = opt;
      b.onclick = function () {
        answers[s.id] = opt;
        [].slice.call(btns.children).forEach(function (x) { x.className = 'answer-btn'; });
        b.className = 'answer-btn ' + cls;
        updateProgress();
      };
      btns.appendChild(b);
    });
    row.appendChild(label);
    row.appendChild(btns);
    return row;
  }

  function updateProgress() {
    const total = Object.keys(answers).length;
    const answered = Object.values(answers).filter(function (v) { return v !== null; }).length;
    progressFill.style.width = (total ? (answered / total * 100) : 0) + '%';
    progressLabel.textContent = answered + ' of ' + total + ' answered';
    if (answered === total && total > 0) showSummary();
  }

  document.getElementById('change-sector-btn').onclick = function () {
    screenSector.style.display = 'block';
    screenCheck.style.display = 'none';
    screenSummary.style.display = 'none';
    setStep(1);
  };

  document.getElementById('restart-btn').onclick = function () {
    document.getElementById('change-sector-btn').onclick();
  };

  // ---- Step 3: summary ----
  function showSummary() {
    let s1 = 0, s2 = 0, s3 = 0, unsure = 0;
    const unsureNames = [];
    const presentItems = [];
    Object.keys(answers).forEach(function (id) {
      const val = answers[id];
      const item = items.find(function (s) { return String(s.id) === String(id); });
      if (val === 'Present') {
        if (item.scope === 'Scope 1') s1++;
        else if (item.scope === 'Scope 2') s2++;
        else s3++;
        presentItems.push({ name: item.name, scope: item.scope });
      } else if (val === 'Unsure') {
        unsure++;
        unsureNames.push(item.name);
      }
    });

    document.getElementById('tile-s1').textContent = s1;
    document.getElementById('tile-s2').textContent = s2;
    document.getElementById('tile-s3').textContent = s3;
    document.getElementById('tile-unsure').textContent = unsure;

    document.getElementById('summary-lede').textContent =
      currentSector + ' \u2014 ' + items.length + ' sources screened.';

    const gapNote = document.getElementById('gap-note');
    if (unsure > 0) {
      gapNote.textContent = 'You marked ' + unsure + ' source' + (unsure > 1 ? 's' : '') +
        ' as unsure \u2014 that\u2019s usually where a completeness gap hides: ' +
        unsureNames.slice(0, 3).join(', ') + (unsureNames.length > 3 ? ', and more.' : '.');
    } else {
      gapNote.textContent = 'No unsure items \u2014 nice. Presence is just step one though: materiality ' +
        'and boundary decisions for each present source still need a proper assessment.';
    }

    document.getElementById('oos-note').textContent = OUT_OF_SCOPE_NOTE;

    screenCheck.style.display = 'none';
    screenSummary.style.display = 'block';
    setStep(3);

    window._lastResult = {
      sector: currentSector,
      scope1_present: s1,
      scope2_present: s2,
      scope3_present: s3,
      unsure_count: unsure,
      unsure_items: unsureNames,
      present_items: presentItems,
      answers: answers,
    };
  }

  // ---- email capture ----
  document.getElementById('email-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const email = document.getElementById('email-input').value;
    const payload = Object.assign({ email: email }, window._lastResult || {});
    fetch('/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(function () {
      document.getElementById('sent-msg').style.display = 'block';
      document.getElementById('email-form').style.display = 'none';
    }).catch(function () {
      document.getElementById('sent-msg').textContent = 'Something went wrong \u2014 please try again.';
      document.getElementById('sent-msg').style.color = '#B06A4F';
      document.getElementById('sent-msg').style.display = 'block';
    });
  });
})();
