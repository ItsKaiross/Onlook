// static/Javascript/admin/audit_trail/audit_trail.js

document.addEventListener('DOMContentLoaded', function () {

    // ── Modal open ──
    window.openAuditModal = function (index) {
        const modal   = document.getElementById(`audit-modal-${index}`);
        const overlay = document.getElementById('audit-overlay');
        if (modal)   modal.classList.add('active');
        if (overlay) overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    };

    // ── Modal close ──
    window.closeAuditModal = function (index) {
        const modal   = document.getElementById(`audit-modal-${index}`);
        const overlay = document.getElementById('audit-overlay');
        if (modal)   modal.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
        document.body.style.overflow = '';
    };

    // ── Close all modals (overlay click) ──
    window.closeAllModals = function () {
        document.querySelectorAll('.audit-modal.active').forEach(m => {
            m.classList.remove('active');
        });
        const overlay = document.getElementById('audit-overlay');
        if (overlay) overlay.classList.remove('active');
        document.body.style.overflow = '';
    };

    // ── ESC key closes modal ──
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            window.closeAllModals();
        }
    });

    // ── Pretty-print JSON in change blocks ──
    document.querySelectorAll('.change-json').forEach(function (el) {
        try {
            const raw    = el.textContent.trim();
            const parsed = JSON.parse(raw);
            el.textContent = JSON.stringify(parsed, null, 2);
        } catch (e) {
            // Not JSON, leave as-is
        }
    });

});