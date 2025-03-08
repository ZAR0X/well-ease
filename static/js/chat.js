document.addEventListener("DOMContentLoaded", () => {
  const input = document.querySelector(".message-input");
  const chatBody = document.querySelector(".chat-body");
  const sendBtn = document.querySelector(".send-btn");
  const emojiBtn = document.querySelector(".emoji-btn");
  const emojiPopup = document.querySelector(".emoji-popup");

  // Function to send a message
  function sendMessage(text, type) {
      if (text.trim() !== "") {
          const message = document.createElement("div");
          message.classList.add("message", type);
          message.textContent = text;
          chatBody.appendChild(message);
          chatBody.scrollTop = chatBody.scrollHeight;
      }
  }

  // Send message when clicking send button
  sendBtn.addEventListener("click", () => {
      if (input.value.trim() !== "") {
          sendMessage(input.value, "sent");
          input.value = "";

          // Bot response after 1 second
          setTimeout(() => {
              sendMessage("Let me help you", "received");
          }, 1000);
      }
  });

  // Send message when pressing Enter key
  input.addEventListener("keypress", (event) => {
      if (event.key === "Enter") {
          sendBtn.click();
      }
  });

  // Toggle emoji popup (positioned above emoji button)
  emojiBtn.addEventListener("click", () => {
      emojiPopup.style.display = emojiPopup.style.display === "block" ? "none" : "block";
  });

  // Send emoji as a message
  emojiPopup.querySelectorAll("button").forEach((emoji) => {
      emoji.addEventListener("click", () => {
          sendMessage(emoji.textContent, "sent");
          emojiPopup.style.display = "none";
      });
  });
});