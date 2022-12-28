// Variables
const roomName = JSON.parse(document.getElementById('room-name').textContent);
const chatLog = document.getElementById("id-chat-log");
const spinner = document.getElementById("id-chatroom-loading-spinner");
let canUserLoadChatMessages = true;


const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/groupchat/'
    + roomName
    + '/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    appendChatMessage(data);
};

chatSocket.onopen = function(e) {
    getChatMessages();
};

chatSocket.onclose = function(e) {
    console.error('ChatSocket closed.');
};

chatSocket.onerror = function(e){
    console.log('ChatSocket error', e);
};

document.getElementById('id-chat-message-input').focus();
document.getElementById('id-chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13 && !e.shiftKey) {  // enter
        document.getElementById('id-chat-message-submit').click();
    }
};

document.querySelector('#id-chat-message-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#id-chat-message-input');
    const message = messageInputDom.value.trim();
    if (message) {
        chatSocket.send(JSON.stringify({
            command: 'send',
            message: message
        }));
    } else {
        showClientErrorModal("You can't send an empty message!");
    }
    messageInputDom.value = '';
};

function appendChatMessage(data, insertDown=true){

    const msg = data['message'] + '\n';
    const msgID = data['msg_id'];
    const username = data['username'] + ": ";
    const profileImageURL = data['profile_image_url'];
    const profileURL = data['profile_url'];
    const msgTimestamp = data['msg_timestamp'];

    // Create chat message element
    let chatLog = document.getElementById("id-chat-log");

    let newMessageDiv = document.createElement("div");
    newMessageDiv.classList.add('d-flex');
    newMessageDiv.classList.add('flex-row');
    newMessageDiv.classList.add('message-container');
    
    let profileImage = document.createElement('img');
    profileImage.addEventListener('click', (e) => window.open(profileURL, '_blank'));
    profileImage.classList.add('profile-image');
    profileImage.classList.add('rounded-circle');
    profileImage.classList.add('img-flui');
    profileImage.src = profileImageURL;
    newMessageDiv.appendChild(profileImage);

    let div1 = document.createElement('div');
    div1.classList.add('d-flex');
    div1.classList.add('flex-column');

    let div2 = document.createElement('div');
    div2.classList.add('d-flex');
    div2.classList.add('flex-row');

    let usernameSpan = document.createElement('span');
    usernameSpan.addEventListener('click', (e) => window.open(profileURL, '_blank'));
    usernameSpan.classList.add('username-span');
    usernameSpan.innerHTML = username;
    div2.appendChild(usernameSpan);

    let timestampSpan = document.createElement("span");
    timestampSpan.innerHTML = msgTimestamp;
    timestampSpan.classList.add("timestamp-span");
    timestampSpan.classList.add("d-flex");
    timestampSpan.classList.add("align-items-center");
    div2.appendChild(timestampSpan);

    div1.appendChild(div2);

    let msgP = document.createElement('p');
    msgP.innerHTML = msg;
    msgP.classList.add('msg-p');
    div1.appendChild(msgP);

    newMessageDiv.appendChild(div1);
    newMessageDiv.setAttribute('msg-id', msgID);
    if (insertDown){
        chatLog.insertBefore(newMessageDiv, chatLog.firstChild);
    } else {
        chatLog.appendChild(newMessageDiv);
    }
};

function showClientErrorModal(message){
    document.getElementById("error-modal-body").innerHTML = message;
    document.getElementById("modal-button").click();
};


function getChatMessages(){
    displayChatRoomLoadingSpinner(true);
    const earliestMsg = document.getElementById("id-chat-log").lastChild;
    const earliestMsgID = earliestMsg ? earliestMsg.getAttribute('msg-id') : null;
    const url = `${window.location.href}/messages/?earliest_msg_id=${earliestMsgID}`;
    fetch(url)
    .then((response) => response.json())
    .then((data) => {
        data.forEach(obj => appendChatMessage(obj, insertDown=false));
        canUserLoadChatMessages = true;
        displayChatRoomLoadingSpinner(false);
    })
    .catch((error) => {
        console.error('Error:', error);
        canUserLoadChatMessages = true;
        displayChatRoomLoadingSpinner(false);
    });
}

// Get the next page of chat messages when scrolls to bottom
chatLog.addEventListener("scroll", function(e){
    if ((Math.abs(chatLog.scrollTop) + 2) >= (chatLog.scrollHeight - chatLog.offsetHeight)
       && canUserLoadChatMessages) {
        canUserLoadChatMessages = false;
        getChatMessages();
    }
});

// Display spinner for loading chat messages
function displayChatRoomLoadingSpinner(display){
    if(display){
        spinner.style.display = "block";
    }
    else {
        spinner.style.display = "none";
    }
}