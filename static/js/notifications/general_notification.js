// Vars
const notificationContainer = document.getElementById("id_general_notifications_container");
const generalNotificationsCountElement = document.getElementById("id_general_notifications_count");
const chatNotificationsCountElement = document.getElementById("id_chat_notifications_count");
const chatNotificationContainer = document.getElementById("id_chat_notifications_container");
const isPrivateChatRoom = window.location.pathname == '/privatechats/' ? true : false;
let canUserLoadGeneralNotifications = true;
let unreadGeneralNotificationsCount = 0;
let unreadChatNotificationsCount = 0;

// Get Cookie by name
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// WebSockets
const notificationSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/notification/'
);

notificationSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const command = data['command'];
    if (command === 'append_new_notification') {
        unreadGeneralNotificationsCount += 1;
        setUnreadGeneralNotificationsCount();
        appendGeneralNotification(data['notification'], insertDown=false);
    } else if (command === 'set_unread_general_notifications_count') {
        unreadGeneralNotificationsCount = data['count']
    } else if (command === 'remove_friendrequest_notification') {
        unreadGeneralNotificationsCount -= unreadGeneralNotificationsCount > 0 ? 1 : 0;
        setUnreadGeneralNotificationsCount();
        const notificationCard = document.getElementById(assignGeneralCardId(data));
        if (notificationCard) {
            notificationCard.remove();
        }
    } else if (command === 'append_new_chat_notification'){
        const chatNotificationID = createChatNotificationID(data['notification']['id'])
        const chatNotificationCard = document.getElementById(chatNotificationID);
        if (chatNotificationCard) {
            chatNotificationCard.remove();
        }
        appendChatNotification(data['notification'], insertDown=false);
    } else if (command === 'update_friend_status'){
        if (isPrivateChatRoom) {
            newstatusSpan = document.createElement('span');
            newstatusSpan.classList.add('friend-message-span', data.status);
            newstatusSpan.innerHTML = data.status;
            statusDiv = document.getElementById(`friend_${data.friend}_status`);
            statusDiv.innerHTML = '';
            statusDiv.appendChild(newstatusSpan);
        }
    }
};

notificationSocket.onopen = function(e) {
    notificationSocket.send(JSON.stringify({
        'command': 'get_unread_general_notifications_count'
    }))    
};

notificationSocket.onclose = function(e) {
    console.error('notification socket closed.');
};

// Fetching Data - General Notifications
function getGeneralNotifications(){
    const earliestNotif = notificationContainer.lastChild;
    const earliestNotifID = earliestNotif ? earliestNotif.id.slice(24) : null;
    const url = `/notifications/general/?earliest_notif_id=${earliestNotifID}`;
    fetch(url)
    .then((response) => response.json())
    .then((data) => {
        data.forEach(obj => appendGeneralNotification(obj));
        canUserLoadGeneralNotifications = true;
    })
    .catch((error) => {
        console.error('Error:', error);
        canUserLoadGeneralNotifications = true;
    });
}
getGeneralNotifications();

// Fetching Data - Chat Notifications
function getChatNotifications(){
    fetch('/privatechats/unread_messages/')
    .then((response) => response.json())
    .then((data) => {
        data.forEach(obj => appendChatNotification(obj));
        // canUserLoadGeneralNotifications = true;
    })
    .catch((error) => {
        console.error('Error:', error);
        // canUserLoadGeneralNotifications = true;
    });
}
getChatNotifications();

/*
    The card that each notification sits in
*/
function createGeneralNotificationCard(){
    const card = document.createElement("div");
    card.classList.add("d-flex", "flex-column", "align-items-start", "general-card", "p-4");
    return card;
}

/*
    Append a general notification to the list.
*/
function appendGeneralNotification(notification, insertDown=true){
    switch(notification['content_type']) {
        case "friendships | friendship":
            card = createFriendshipElement(notification);
            break;
        case "friendships | friend request":
            card = createFriendRequestElement(notification);
            break;

        default:
            console.error(`Unkonwn notification content_type: ${notification['content_type']}`);
    }
    if (insertDown) {
        notificationContainer.appendChild(card);
    } else {
        notificationContainer.insertBefore(card, notificationContainer.firstChild);
    }
}

/*
    Append a unread private chat message notification
*/
function appendChatNotification(notification, insertDown=true){
    const card = createUnreadChatRoomMessagesCard(notification);
    if (insertDown) {
        chatNotificationContainer.appendChild(card);
    } else {
        chatNotificationContainer.insertBefore(card, chatNotificationContainer.firstChild);
    }
    unreadChatNotificationsCount += 1;
    setUnreadChatNotificationsCount();
    // if current locatin is private chat room location then update the count of related friend uread messages
    if (isPrivateChatRoom) {
        handleFriendUnreadMessageCounter(notification);
    };
}

function createFriendshipElement(notification){
    card = createGeneralNotificationCard();
    card.id = assignGeneralCardId(notification);
    card.addEventListener("click", function(){
        window.location.href = notification['profile_url'];
    })

    const div1 = document.createElement("div");
    div1.classList.add("d-flex", "flex-row", "align-items-start");

    img = createProfileImageThumbnail(notification['image_url']);
    div1.appendChild(img);

    span = document.createElement("span")
    span.classList.add("align-items-start", "pt-1", "m-auto");
    if(notification['verb'].length > 50){
        span.innerHTML = notification['verb'].slice(0, 50) + "...";
    }
    else{
        span.innerHTML = notification['verb'];
    }
    div1.appendChild(span);
    card.appendChild(div1);
    card.appendChild(createGeneralTimestampElement(notification['timestamp']));
    return card;
}

/*
    Create a Notification Card for a FriendRequest payload
*/
function createFriendRequestElement(notification){
    card = createGeneralNotificationCard()
    card.id = assignGeneralCardId(notification)
    card.addEventListener("click", function(){
        window.location.href = notification['profile_url'];
    })

    div1 = document.createElement("div")
    div1.classList.add("d-flex", "flex-row", "align-items-start")
    
    img = createProfileImageThumbnail(notification['image_url']);
    div1.appendChild(img)

    span = document.createElement("span")
    span.classList.add("m-auto")
    span.innerHTML = notification['verb']
    div1.appendChild(span)
    card.appendChild(div1)

    div2 = document.createElement("div")
    div2.classList.add("d-flex", "flex-row", "mt-2")

    pos_action = document.createElement("a")
    pos_action.classList.add("btn", "btn-primary", "mr-2")
    pos_action.innerHTML = "Accept"
    pos_action.addEventListener("click", function(e){
        e.stopPropagation();
        handleFriendRequest(notification['content_object_id'], accept=true, card.id);
    })
    div2.appendChild(pos_action)

    neg_action = document.createElement("a")
    neg_action.classList.add("btn", "btn-secondary")
    neg_action.innerHTML = "Decline"
    neg_action.addEventListener("click", function(e){
        e.stopPropagation();
        handleFriendRequest(notification['content_object_id'], accept=false, card.id);
    })
    div2.appendChild(neg_action)
    card.appendChild(div2)

    card.appendChild(createGeneralTimestampElement(notification['timestamp']))
    return card
}

/*
    The card that each notification sits in
*/
function createChatNotificationCard(){
    var card = document.createElement("div")
    card.classList.add("d-flex", "flex-column", "align-items-start", "chat-card", "p-4")
    return card
}

function createUnreadChatRoomMessagesCard(notification){
    card = createChatNotificationCard()
    card.id = createChatNotificationID(notification['id'])
    card.addEventListener("click", function(){
        setChatNotificationsAsRead(notification['id']);
    })

    var div1 = document.createElement("div")
    div1.classList.add("d-flex", "flex-row", "align-items-start")

    img = createProfileImageThumbnail(notification['sender_profile_image'])
    div1.appendChild(img)

    var div2 = document.createElement("div")
    div2.classList.add("d-flex", "flex-column")
    
    var title = document.createElement("span")
    title.classList.add("align-items-start")
    title.innerHTML = notification['sender_username']
    div2.appendChild(title)

    var chatRoomMessage = document.createElement("span")
    chatRoomMessage.classList.add("align-items-start", "pt-1", "small", "notification-chatroom-msg")
    if(notification['most_recent_message'].length > 50){
        chatRoomMessage.innerHTML = notification['most_recent_message'].slice(0, 50) + "..."
    } else {
        chatRoomMessage.innerHTML = notification['most_recent_message']
    }
    div2.appendChild(chatRoomMessage)
    div1.appendChild(div2)
    card.appendChild(div1)
    card.appendChild(createGeneralTimestampElement(notification['most_recent_message_timestamp']))
    return card
}

// Handle Friend Request
function handleFriendRequest(requestID, accept, cardID){
    url = `/friendships/handle_friend_request/${requestID}/`;
    let data = new FormData();
    data.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    data.append('accept', accept);
    fetch(url, 
        {
            method: 'POST',
            body: data
        },
    )
    .then((response) => response.text())
    .then((data) => {
        location.reload();
    })
    .catch((error) => {
        console.error('Error:', error);
    });
    document.getElementById(cardID).remove();
}

/*
    Circular image icon that can be in a notification card
*/
function createProfileImageThumbnail(imageURL){
    const img = document.createElement("img");
    img.classList.add("notification-thumbnail-image", "img-fluid", "rounded-circle", "mr-2");
    img.src = imageURL;
    return img;
}

/*
    Timestamp at the bottom of each notification card
*/
function createGeneralTimestampElement(notificationTimestamp){
    const timestamp = document.createElement("p");
    timestamp.classList.add("small", "pt-2", "timestamp-text");
    timestamp.setAttribute('isotime', notificationTimestamp);
    timestamp.innerHTML = dateTimeToYMWDHMS(notificationTimestamp);
    return timestamp;
}
/*
    Calculate the seconds, minutes, hours, days, weeks and ... difference between notification and now datetime
*/
function dateTimeToYMWDHMS(datetime) {
    const startDate = new Date(datetime);
    const endDate = new Date();
    const seconds = (endDate.getTime() - startDate.getTime()) / 1000;
    const s = Math.floor(seconds % 60);
    const m = Math.floor(seconds % 3600 / 60);
    const h = Math.floor(seconds % (3600*24) / 3600);
    const d = Math.floor(seconds % ((3600*24)*7) / (3600*24));
    const w = Math.floor(seconds % ((3600*24)*30) / ((3600*24)*7));
    const M = Math.floor(seconds % (((3600*24)*30)*12) / ((3600*24)*30));
    const y = Math.floor(seconds / (((3600*24)*30)*12));
    const yDisplay = y > 0 ? y + (y == 1 ? " year, ": " years, ") : "";
    const MDisplay = M > 0 ? M + (M == 1 ? " month, ": " months, ") : "";
    const wDisplay = w > 0 ? w + (w == 1 ? " week, ": " weeks, ") : "";
    const dDisplay = d > 0 ? d + (d == 1 ? " day, " : " days, ") : "";
    const hDisplay = h > 0 ? h + (h == 1 ? " hour, " : " hours, ") : "";
    const mDisplay = m > 0 ? m + (m == 1 ? " minute, " : " minutes, ") : "";
    const sDisplay = s > 0 ? s + (s == 1 ? " second" : " seconds") : "";
    return yDisplay + MDisplay + wDisplay + dDisplay + hDisplay + mDisplay + sDisplay;
}

/*
    Update time of notification cards repeatedly every 5 seconds
*/
function updateNotificationsTime() {
    let listItems = document.querySelectorAll('.timestamp-text');
    listItems = Array.from(listItems);
    listItems.forEach(item => {
        item.innerHTML = dateTimeToYMWDHMS(item.getAttribute('isotime'));
    })
}
setInterval(updateNotificationsTime, 5000);

/*
    Sets the scroll listener for when user scrolls to bottom of notification menu.
    It will retrieve the next page of results.
*/
const menu = document.getElementById("id_general_notifications_container")
menu.addEventListener("scroll", function(e){
    if ((menu.scrollTop) >= (menu.scrollHeight - menu.offsetHeight) && canUserLoadGeneralNotifications) {
        canUserLoadGeneralNotifications = false;
        getGeneralNotifications();
    }
});

/*
    Set the number of unread notifications.
*/
function setUnreadGeneralNotificationsCount(){
    if(unreadGeneralNotificationsCount > 0){
        generalNotificationsCountElement.style.background = "red"
        generalNotificationsCountElement.style.display = "block"
        generalNotificationsCountElement.innerHTML = unreadGeneralNotificationsCount
    } else {
        generalNotificationsCountElement.style.background = "transparent"
        generalNotificationsCountElement.style.display = "none"
    }
}

function setUnreadChatNotificationsCount(){
    if(unreadChatNotificationsCount > 0){
        chatNotificationsCountElement.style.background = "red"
        chatNotificationsCountElement.style.display = "block"
        chatNotificationsCountElement.innerHTML = unreadChatNotificationsCount
    } else {
        chatNotificationsCountElement.style.background = "transparent"
        chatNotificationsCountElement.style.display = "none"
    }
}

/*
    Sets all the notifications currently visible as "read"
*/
function setGeneralNotificationsAsRead(){
    notificationSocket.send(JSON.stringify({
        "command": "mark_notifications_read",
    }));
    unreadGeneralNotificationsCount = 0;
    setUnreadGeneralNotificationsCount();
}

// Set chat notifications as read
function setChatNotificationsAsRead(ID) {
    notificationSocket.send(JSON.stringify({
        command: "mark_chat_notification_read",
        id: ID
    }));
    document.getElementById(createChatNotificationID(ID)).remove();
    unreadChatNotificationsCount -= unreadChatNotificationsCount > 0 ? 1 : 0;
    setUnreadChatNotificationsCount();
}

// Event listeners
document.getElementById('id_notification_dropdown_toggle').addEventListener('click', e => {
    setGeneralNotificationsAsRead();
})

//  Helpers for generating IDs 
function assignGeneralCardId(notification){
    return "id_general_notification_" + notification['notification_id']
}

function createChatNotificationID(ID) {
    return `id_chat_notification_${ID}`
}


// Handle the unread chat message notifications in private chat room friends list
function handleFriendUnreadMessageCounter(notification){
    const friendUsername = notification['sender_username'];
    const counterSpan = document.getElementById(`${friendUsername}_unread_msgs_count`);
    counterSpan.setAttribute('notificationid', notification.id);
    counterSpan.innerHTML = notification.count;
}
