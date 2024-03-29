// Variables
let chatSocket = null;
const chatLog = document.getElementById("id_chat_log");
const spinner = document.getElementById("id_chatroom_loading_spinner");
const chatMessageInput = document.getElementById("id_chat_message_input");
const chatSubmitButton = document.getElementById("id_chat_message_submit");
const md = window.markdownit();
let canUserLoadChatMessages = true;
let selectedFriendDiv = null;
let selectedFriendUsername = null;
let selectedFriendProfileURL = null;



// Select related friend if user redirected to this page from someones profile
let url = new URL(window.location.href);
let friendUsername = url.searchParams.get('friend_username');
if (friendUsername) {
    document.getElementById(`id_friend_container_${friendUsername}`).click();
}


function onSelectFriend(username, profileURL) {
    clearHighlightedFriend();
    chatLog.innerHTML = ""      // clear chat log 
    if (chatSocket !== null) {
        chatSocket.close();
    }
    selectedFriendDiv = document.getElementById(`id_friend_container_${username}`);
    selectedFriendUsername = username;
    selectedFriendProfileURL = profileURL;
    setupWebSocket(username);
    chatMessageInput.disabled = false;
    chatSubmitButton.disabled = false;
    highlightFriend();
    handleUnreadMessageCount();
}

function setupWebSocket(roommate) {
    chatSocket = new WebSocket(
        window.location.protocol === 'https:' ? 'wss://' : 'ws://'
        + window.location.host
        + '/ws/privatechat/'
        + roommate
        + '/'
    );
    
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const msgType = data['type'];
        if (msgType === 'chat_message'){
            appendChatMessage(data);
        } else if (msgType === 'room_online_users_count') {
            setRoomOnlineUsersCount(data);
        }
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
}


// document.getElementById('id_chat_message_input').focus();
document.getElementById('id_chat_message_input').onkeyup = function(e) {
    if (e.keyCode === 13 && !e.shiftKey) {  // enter
        document.getElementById('id_chat_message_submit').click();
    }
};

document.querySelector('#id_chat_message_submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#id_chat_message_input');
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
    const earliestMsg = document.getElementById("id_chat_log").lastChild;
    const earliestMsgID = earliestMsg ? earliestMsg.getAttribute('msg-id') : null;
    const url = `/privatechats/room/${selectedFriendUsername}/messages/?earliest_msg_id=${earliestMsgID}`;
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

// Set count of online users in this chat room
function setRoomOnlineUsersCount(data){
    element = document.getElementById("id_connected_users");
    element.innerHTML = data['room_online_users_count'];
}

function highlightFriend(){
    // select new friend
    selectedFriendDiv.style.background = "#f2f2f2"
    document.getElementById("id_other_username").innerHTML = selectedFriendUsername;
    document.getElementById("id_other_user_profile_image").classList.remove("d-none");
    document.getElementById("id_user_info_container").href = selectedFriendProfileURL;
    document.getElementById("id_other_user_profile_image").src = document
        .getElementById(`id_friend_img_${selectedFriendUsername}`).getAttribute('src');
}

function clearHighlightedFriend(){
    if (selectedFriendDiv !== null) {
        selectedFriendDiv.style.background = ""
        // clear the profile image and username of current chat
        document.getElementById("id_other_user_profile_image").classList.add("d-none")
        document.getElementById("id_other_user_profile_image").src = ''
        document.getElementById("id_other_username").innerHTML = ""
    }
}

// Handle unread chat messages count
function handleUnreadMessageCount(){
    const counterSpan = document.getElementById(`${selectedFriendUsername}_unread_msgs_count`);
    if (counterSpan.innerHTML) {
        const notificationID = counterSpan.getAttribute('notificationid');
        // send set unread messages as read command via notification websocket
        setChatNotificationsAsRead(notificationID);
        counterSpan.innerHTML = '';
        document.getElementById(`${selectedFriendUsername}_last_message_span`).innerHTML = '';
    }
}