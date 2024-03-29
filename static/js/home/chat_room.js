// Variables
const roomName = 'public';
const chatLog = document.getElementById("id-chat-log");
const spinner = document.getElementById("id-chatroom-loading-spinner");
let canUserLoadChatMessages = true;
const md = window.markdownit();


// document.getElementById('id-chat-message-input').focus();
document.getElementById('id-chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13 && !e.shiftKey) {  // enter
        document.getElementById('id-chat-message-submit').click();
    }
};

document.querySelector('#id-chat-message-submit').onclick = function(e) {
    showClientErrorModal('Please login first and then send your message.');
}


function appendChatMessage(data, insertDown=true){
    const msg = data['message'] + '\n';
    const msgID = data['msg_id'];
    const username = data['username'] + ": ";
    const profileImageURL = data['profile_image_url'];
    const profileURL = data['profile_url'];
    const msgTimestamp = data['msg_timestamp'];

    // Create chat message element
    const newMessageDiv = document.createElement("div");
    newMessageDiv.classList.add('d-flex');
    newMessageDiv.classList.add('flex-row');
    newMessageDiv.classList.add('message-container');
    
    const profileImage = document.createElement('img');
    profileImage.addEventListener('click', (e) => window.open(profileURL, '_blank'));
    profileImage.classList.add('profile-image');
    profileImage.classList.add('rounded-circle');
    profileImage.classList.add('img-flui');
    profileImage.src = profileImageURL;
    newMessageDiv.appendChild(profileImage);

    const div1 = document.createElement('div');
    div1.classList.add('d-flex');
    div1.classList.add('flex-column');

    const div2 = document.createElement('div');
    div2.classList.add('d-flex');
    div2.classList.add('flex-row');

    const usernameSpan = document.createElement('span');
    usernameSpan.addEventListener('click', (e) => window.open(profileURL, '_blank'));
    usernameSpan.classList.add('username-span');
    usernameSpan.innerHTML = username;
    div2.appendChild(usernameSpan);

    const timestampSpan = document.createElement("span");
    timestampSpan.setAttribute('isotime', msgTimestamp);
    timestampSpan.innerHTML = formatDatetime(msgTimestamp);
    timestampSpan.classList.add("timestamp-span");
    timestampSpan.classList.add("d-flex");
    timestampSpan.classList.add("align-items-center");
    div2.appendChild(timestampSpan);

    div1.appendChild(div2);

    const msgP = document.createElement('p');
    msgP.innerHTML = md.render(msg);
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

/*
    Format messages date
*/
function formatDatetime(isoDatetime){
    const inputDate = new Date(isoDatetime);
    const today = new Date();
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);

    if(inputDate.toDateString() === today.toDateString()){
        const seconds = (today.getTime() - inputDate.getTime()) / 1000;
        const s = Math.floor(seconds % 60);
        const m = Math.floor(seconds % 3600 / 60);
        const h = Math.floor(seconds / 3600);
        const hDisplay = h > 0 ? h + (h == 1 ? " hour" : " hours") : "";
        if(hDisplay){
            const todayTime = inputDate.toLocaleTimeString(
                'en-us',
                {hour: '2-digit', minute: '2-digit'}
            )
            return `today at ${todayTime}`;
        };
        const mDisplay = m > 0 ? m + (m == 1 ? " minute" : " minutes") : "";
        if(mDisplay){return `${mDisplay} ago`};
        const sDisplay = s > 0 ? s + (s == 1 ? " second" : " seconds") : "";
        if(sDisplay){return `${sDisplay} ago`};
        return 'just now';

    } else if (inputDate.toDateString() === yesterday.toDateString()) {
        const yesterdayTime = inputDate.toLocaleTimeString(
            'en-us',
            {hour: '2-digit', minute: '2-digit'}
        )
        return `Yesterday at ${yesterdayTime}`

    } else if(inputDate.getFullYear() === today.getFullYear()){
        return inputDate.toLocaleDateString(
            'en-us',
            {weekday:'long', month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'}
        )
    }
    
    return inputDate.toLocaleDateString(
        'en-us',
        {year:'numeric', month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'}
    )
}

// Update time of messages repeatedly every 5 seconds
function updateMessagesTime() {
    let listItems = document.querySelectorAll('.timestamp-span');
    listItems = Array.from(listItems);
    listItems.forEach(item => {
        item.innerHTML = formatDatetime(item.getAttribute('isotime'));
    })
}
setInterval(updateMessagesTime, 5000);

function showClientErrorModal(message){
    document.getElementById("error-modal-body").innerHTML = message;
    document.getElementById("modal-button").click();
};


function getChatMessages(){
    displayChatRoomLoadingSpinner(true);
    const earliestMsg = document.getElementById("id-chat-log").lastChild;
    const earliestMsgID = earliestMsg ? earliestMsg.getAttribute('msg-id') : null;
    const url = `/public_messages/?earliest_msg_id=${earliestMsgID}`;
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
getChatMessages();

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

// Set count of online users in this chat room
function setRoomOnlineUsersCount(data){
    element = document.getElementById("id-connected-users");
    element.innerHTML = data['room_online_users_count'];
}