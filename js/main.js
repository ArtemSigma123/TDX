window.onload = function() {
    const wrapper = document.getElementById('main-wrapper');
    const chatTrigger = document.getElementById('chat-trigger');
    const backBtn = document.getElementById('mobile-back');
    const menuOpen = document.getElementById('mob-menu-open');
    const menuClose = document.getElementById('mob-menu-close');
    const sidebar = document.getElementById('sidebar');

    // Клик по чату
    if(chatTrigger) {
        chatTrigger.addEventListener('click', function() {
            wrapper.classList.add('chat-opened');
        });
    }

    // Клик назад
    if(backBtn) {
        backBtn.addEventListener('click', function() {
            wrapper.classList.remove('chat-opened');
        });
    }

    // Меню
    if(menuOpen) {
        menuOpen.onclick = function() { sidebar.classList.add('active'); };
    }
    if(menuClose) {
        menuClose.onclick = function() { sidebar.classList.remove('active'); };
    }

    // Кошелек
    const wBtn = document.getElementById('wallet-btn');
    const wModal = document.getElementById('wallet-modal');
    if(wBtn) wBtn.onclick = () => wModal.style.display = 'flex';
    if(document.getElementById('close-wallet')) {
        document.getElementById('close-wallet').onclick = () => wModal.style.display = 'none';
    }

    // Отправка сообщений
    const input = document.getElementById('msg-input');
    const sendBtn = document.getElementById('send-btn');
    const chatBox = document.getElementById('chat-box');

    async function send() {
        if(!input.value.trim()) return;
        const res = await fetch('/send_message', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: input.value})
        });
        if(res.ok) {
            location.reload(); // Перезагрузим, чтобы увидеть сообщение из базы
        }
    }
    if(sendBtn) sendBtn.onclick = send;
};

