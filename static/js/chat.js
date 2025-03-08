document.addEventListener("DOMContentLoaded", () => {
  const input = document.querySelector(".message-input");
  const chatBody = document.querySelector(".chat-body");
  const sendBtn = document.querySelector(".send-btn");
  const emojiBtn = document.querySelector(".emoji-btn");
  const emojiPopup = document.querySelector(".emoji-popup");
  sessionStorage.removeItem("chatHistory")

let audio1 = new Audio("https://s3-us-west-2.amazonaws.com/s.cdpn.io/242518/clickUp.mp3");
  
const apiUrl = "https://duckgpt.iriszarox.workers.dev/chat/";

function saveMessage(content, role, error=false) {
  const history = JSON.parse(sessionStorage.getItem("chatHistory") || '[]');
  history.push({ role: role, content: content, error: error});
  sessionStorage.setItem("chatHistory", JSON.stringify(history));
}

  
  function sendMessage(text, type) {
        if (type === "recieve") {}
      if (text !== "") {
          const message = document.createElement("div");
          message.classList.add("message", type);
          message.textContent = text;
          
          let audio3 = new Audio(
            "https://downloadwap.com/content2/mp3-ringtones/tone/2020/alert/preview/56de9c2d5169679.mp3"
          );
          audio3.load();
          audio3.play();
          chatBody.appendChild(message);
          chatBody.scrollTop = chatBody.scrollHeight;
      }
  }
  function userResponse() {
    if (sessionStorage.length == 0) {
      saveMessage('Hello, I would like you to act as a character named Dr. Well. Dr. Well is a highly intelligent and compassionate health expert who is dedicated to helping users with health-related questions and mental well-being. When users reach out with problems or questions related to their health or mental wellness, Dr. Well should use their knowledge and also search the web for the best possible solutions and advice. However, if users bring up topics unrelated to health or mental well-being, Dr. Well should kindly steer the conversation back to relevant topics and remind them not to deviate into irrelevant discussions. Dr. Well\'s goal is always to assist users in maintaining or improving their health, and anything outside that scope should be gently dismissed as an inappropriate topic for conversation.\n\nFor example:\n If someone asks a question about fitness, nutrition, stress management, or mental health, Dr. Well should respond helpfully, providing suggestions or directing them to online resources. If the conversation shifts to topics like entertainment, personal opinions, or anything non-health related, Dr. Well should acknowledge the change and steer the conversation back to health-related topics, reminding the user to focus on improving well-being. Remember: Dr. Well should always be polite, helpful, and dedicated to guiding the user toward solutions for better health and mental wellness.', 'user')
    }
  
    let userText = document.getElementById("textInput").value;
    
    if (userText == "") {
      alert("Please type something!");
    } else {
        
        sendMessage(userText, "sent");
      let audio3 = new Audio(
        "https://prodigits.co.uk/content/ringtones/tone/2020/alert/preview/4331e9c25345461.mp3"
      );
      audio3.load();
      audio3.play();
  
      document.getElementById("textInput").value = "";
      saveMessage(userText, 'user')
      // Call the NLP model for generating the chatbot response
      const history = JSON.parse(sessionStorage.getItem("chatHistory") || "[]");
      // const model = "gpt-4o-mini";
      const userHistory = (history.filter((message) => (message.role === "user" && !message.error))).map(({ error, ...rest }) => rest);
      console.log(userHistory)
      const params = new URLSearchParams({
        prompt: userText,
        // model: model,
        history: JSON.stringify(userHistory),
      });
      fetch(`${apiUrl}?${params.toString()}`)
        .then((response) => {
          return response.json().then((data) => {
            saveMessage(data.response, 'api')
            return data.response});
        })
        .then((chatbotResponse) => {
            sendMessage(chatbotResponse, "received")
          let audio3 = new Audio(
            "https://downloadwap.com/content2/mp3-ringtones/tone/2020/alert/preview/56de9c2d5169679.mp3"
          );
          audio3.load();
          audio3.play();
  
        })
        .catch((error) => {
          console.log(error);
        });
    }
  }
  

  sendBtn.addEventListener("click", () => {
      if (input.value.trim() !== "") {
          userResponse();
      }
  });

  
  input.addEventListener("keypress", (event) => {
      if (event.key === "Enter") {
          sendBtn.click();
      }
  });

  

  emojiBtn.addEventListener("click", () => {
      emojiPopup.style.display = emojiPopup.style.display === "block" ? "none" : "block";
  });

  
  emojiPopup.querySelectorAll("button").forEach((emoji) => {
      emoji.addEventListener("click", () => {
          sendMessage(emoji.textContent, "sent");
          emojiPopup.style.display = "none";
      });
  });
});