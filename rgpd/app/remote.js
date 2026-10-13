/* COTOMA — couche de données pour l'hébergement OVH.
   Remplace la base fournie par claude.ai : même interface (collection, doc, onSnapshot, set, update, delete, add),
   mais les données vont dans api.php, protégé par mot de passe. */
(function () {
  'use strict';
  const API = 'api.php';
  const listeners = { coll: {}, doc: {} };
  let timer = null, lastAt = '';

  async function call(action, payload, method) {
    const opts = { method: method || 'POST', credentials: 'same-origin', headers: { 'X-Cotoma': '1', 'Content-Type': 'application/json' } };
    if (opts.method === 'POST') opts.body = JSON.stringify(Object.assign({ action }, payload || {}));
    const url = opts.method === 'GET' ? API + '?action=' + encodeURIComponent(action) : API;
    const r = await fetch(url, opts);
    let j = null; try { j = await r.json(); } catch (e) { j = null; }
    if (r.status === 401 && action !== 'login') { showLogin(); throw { code: 'not_granted', message: 'Connexion requise.' }; }
    if (!r.ok) throw { code: r.status === 409 ? 'invalid_argument' : r.status === 429 ? 'resource_exhausted' : 'unavailable', message: (j && j.error) || ('HTTP ' + r.status) };
    return j;
  }
  function snapDoc(id, data) { const frozen = data ? Object.freeze(Object.assign({}, data)) : undefined; return { id, exists: !!data, data: () => frozen, metadata: { fromCache: false, hasPendingWrites: false } }; }
  async function refresh() {
    let res; try { res = await call('all'); } catch (e) { Object.values(listeners.coll).forEach(l => l.err && l.err(e)); return; }
    lastAt = res.at;
    const C = res.collections || {};
    for (const [c, l] of Object.entries(listeners.coll)) {
      const docs = (C[c] || []).map(d => snapDoc(d.id, d.data));
      l.fn({ docs, size: docs.length, empty: !docs.length, docChanges: () => docs.map((doc, i) => ({ type: 'added', doc, oldIndex: -1, newIndex: i })), metadata: { fromCache: false, hasPendingWrites: false } });
    }
    for (const [p, l] of Object.entries(listeners.doc)) {
      const [c, id] = p.split('/'); const d = (C[c] || []).find(x => x.id === id);
      l.fn(snapDoc(id, d ? d.data : null));
    }
  }
  function schedule() { if (timer) return; timer = setTimeout(() => { timer = null; refresh(); }, 50); }
  function newId() { const a = 'abcdefghijklmnopqrstuvwxyz0123456789'; let s = ''; const r = new Uint8Array(20); crypto.getRandomValues(r); r.forEach(b => s += a[b % a.length]); return s; }
  function docRef(path) {
    const parts = path.split('/'); if (parts.length !== 2) throw new TypeError('Chemin de document invalide : ' + path);
    const [collection, id] = parts;
    return {
      id, path,
      async get() { const res = await call('list', { collection }); const d = (res.docs || []).find(x => x.id === id); return snapDoc(id, d ? d.data : null); },
      async set(data) { await call('set', { collection, id, data }); schedule(); },
      async update(data) { await call('update', { collection, id, data }); schedule(); },
      async delete() { await call('delete', { collection, id }); schedule(); },
      onSnapshot(fn, err) { listeners.doc[path] = { fn, err }; schedule(); return () => { delete listeners.doc[path]; }; },
      collection(sub) { return collRef(path + '/' + sub); }
    };
  }
  function collRef(path) {
    if (path.split('/').length % 2 === 0) throw new TypeError('Chemin de collection invalide : ' + path);
    const collection = path;
    const q = {
      path,
      where() { return q; }, orderBy() { return q; }, limit() { return q; },
      async get() { const res = await call('list', { collection }); const docs = (res.docs || []).map(d => snapDoc(d.id, d.data)); return { docs, size: docs.length, empty: !docs.length, docChanges: () => [], metadata: { fromCache: false, hasPendingWrites: false } }; },
      onSnapshot(fn, err) { listeners.coll[collection] = { fn, err }; schedule(); return () => { delete listeners.coll[collection]; }; },
      doc(id) { return docRef(collection + '/' + (id || newId())); },
      async add(data) { const ref = docRef(collection + '/' + newId()); await ref.set(data); return ref; }
    };
    return q;
  }
  const db = { doc: docRef, collection: collRef };
  const user = { async can() { return true; }, isOwner() { return true; }, canEdit() { return true; }, async id() { return 'proprietaire'; } };
  const downloads = { async save({ filename, data }) { const blob = data instanceof Blob ? data : new Blob([data]); const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = filename; document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 2000); return { status: 'saved' }; } };

  /* Écran de connexion */
  let overlay = null;
  function showLogin(msg) {
    if (!overlay) {
      overlay = document.createElement('div'); overlay.id = 'login';
      overlay.innerHTML = '<form class="login-box" id="login-form"><p class="eyebrow">COTOMA</p><h2>Tableau de bord</h2><label for="pw">Mot de passe</label><input id="pw" type="password" autocomplete="current-password" required autofocus><button class="btn" type="submit">Entrer</button><p class="note" id="login-msg"></p></form>';
      document.body.appendChild(overlay);
      overlay.querySelector('form').addEventListener('submit', async e => {
        e.preventDefault(); const b = overlay.querySelector('button'); b.disabled = true;
        try { await call('login', { password: overlay.querySelector('#pw').value }); hideLogin(); if (resolveBoot) { resolveBoot(); resolveBoot = null; } refresh(); }
        catch (err) { overlay.querySelector('#login-msg').textContent = err.message || 'Erreur.'; }
        b.disabled = false;
      });
    }
    overlay.hidden = false; if (msg) overlay.querySelector('#login-msg').textContent = msg;
  }
  function hideLogin() { if (overlay) overlay.hidden = true; }
  let resolveBoot = null;

  window.remoteBoot = async function () {
    let st = null; try { st = await call('status', null, 'GET'); } catch (e) { st = null; }
    if (!st) { showLogin('Le serveur ne répond pas. Vérifie que api.php est bien en ligne.'); }
    else if (st.setup) { showLogin('Définis d\'abord un mot de passe dans config.php sur le serveur.'); }
    else if (!st.auth) { showLogin(); }
    if (!st || !st.auth) await new Promise(res => { resolveBoot = res; });
    document.addEventListener('visibilitychange', () => { if (!document.hidden) refresh(); });
    setInterval(() => { if (!document.hidden) refresh(); }, 30000);
    return [db, user, downloads];
  };
  window.cotomaLogout = async function () { try { await call('logout'); } catch (e) {} location.reload(); };
})();
