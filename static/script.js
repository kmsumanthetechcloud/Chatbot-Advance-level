function toggleChat() {
  const box = document.getElementById('chatbot-box');
  const isHidden = box.style.display === 'none' || box.style.display === '';
  box.style.display = isHidden ? 'flex' : 'none';
}

document.addEventListener('DOMContentLoaded', function () {
  document.getElementById('chatbot-icon').addEventListener('click', toggleChat);

  const form = document.getElementById('chat-form');
  const input = document.getElementById('user-query');
  const chatBody = document.getElementById('chat-body');

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    const question = input.value.trim();
    if (!question) return;

    // Show user's message
    const userMsg = document.createElement('div');
    userMsg.className = 'message user-msg';
    userMsg.textContent = question;
    chatBody.appendChild(userMsg);
    input.value = '';

    // Send question to Flask
    try {
      const response = await fetch("/", {
        method: "POST",
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({ query: question })
      });

      const html = await response.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      const botResponse = doc.querySelector('.bot-msg');

      if (botResponse) {
        chatBody.appendChild(botResponse);
      } else {
        const fallback = document.createElement('div');
        fallback.className = 'message bot-msg error-msg';
        fallback.textContent = 'Something went wrong. Try again.';
        chatBody.appendChild(fallback);
      }
    } catch (error) {
      const fallback = document.createElement('div');
      fallback.className = 'message bot-msg error-msg';
      fallback.textContent = 'Failed to connect to server.';
      chatBody.appendChild(fallback);
    }

    chatBody.scrollTop = chatBody.scrollHeight;
  });
});
