document.querySelectorAll('.rename-toggle-btn').forEach(btn => {
  btn.addEventListener('click', e => {
    e.stopPropagation();
    const id = btn.dataset.id;
    const row = document.getElementById('rename-row-' + id);
    if (!row) return;
    const visible = row.style.display !== 'none';
    row.style.display = visible ? 'none' : 'block';
    if (!visible) document.getElementById('rename-input-' + id)?.focus();
  });
});

document.querySelectorAll('.rename-cancel-btn').forEach(btn => {
  btn.addEventListener('click', e => {
    e.stopPropagation();
    const row = document.getElementById('rename-row-' + btn.dataset.id);
    if (row) row.style.display = 'none';
  });
});

document.querySelectorAll('.rename-confirm-btn').forEach(btn => {
  btn.addEventListener('click', async e => {
    e.stopPropagation();
    const id = btn.dataset.id;
    const input = document.getElementById('rename-input-' + id);
    const nickname = input ? input.value.trim() : '';
    if (nickname.length > 12) {
      showAlert('Le surnom ne peut pas dépasser 12 caractères.', 'danger');
      return;
    }
    btn.disabled = true;
    try {
      const data = await post('/api/rename-pokemon/', { pokemon_id: id, nickname });
      if (data.success) {
        showAlert('✅ Renommé en "' + (data.nickname || '(aucun surnom)') + '".', 'success');
        const row = document.getElementById('rename-row-' + id);
        if (row) row.style.display = 'none';
        setTimeout(() => location.reload(), 900);
      } else {
        showAlert(data.error || 'Erreur lors du renommage.', 'danger');
      }
    } catch {
      showAlert('Erreur réseau.', 'danger');
    } finally {
      btn.disabled = false;
    }
  });
});

document.querySelectorAll('.rename-input').forEach(input => {
  input.addEventListener('keydown', e => {
    const rowId = input.closest('[id^="rename-row-"]').id.replace('rename-row-', '');
    if (e.key === 'Enter') {
      e.preventDefault();
      document.querySelector('.rename-confirm-btn[data-id="' + rowId + '"]')?.click();
    } else if (e.key === 'Escape') {
      document.querySelector('.rename-cancel-btn[data-id="' + rowId + '"]')?.click();
    }
  });
});
