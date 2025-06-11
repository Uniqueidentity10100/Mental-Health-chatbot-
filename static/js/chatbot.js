$(document).ready(function() {
    var chatState = 'initial';
    const CHAT_STATES = {
        INITIAL: 'initial',
        NAME: 'name',
        AGE: 'age',
        OCCUPATION: 'occupation',
        PAST_DIAGNOSIS: 'past_diagnosis',
        MOOD: 'mood',
        FREE_CHAT: 'free_chat'
    };
    
    var userData = {
        name: '',
        age: '',
        occupation: '',
        pastDiagnosis: '',
        mood: '',
        moodReason: ''
    };

    function appendMessage(message, type = 'bot') {
        if (!message) return; // Don't append undefined messages
        
        var messageDiv = $('<div>').addClass('message');
        messageDiv.addClass(type === 'user' ? 'user-message' : 'bot-message');
        
        // Split message by newlines and create paragraphs
        var paragraphs = message.split('\n');
        paragraphs.forEach(function(paragraph) {
            if (paragraph.trim() === '') {
                messageDiv.append($('<br>')); // Add empty line
            } else if (paragraph.startsWith('•')) {
                // Create a special div for bullet points with proper indentation
                var bulletPoint = $('<div>').addClass('bullet-point').text(paragraph);
                messageDiv.append(bulletPoint);
            } else {
                messageDiv.append($('<p>').text(paragraph));
            }
        });
        
        $('#chat-messages').append(messageDiv);
        $('#chat-messages').scrollTop($('#chat-messages')[0].scrollHeight);
    }

    function createOptionButtons(options) {
        var buttonsDiv = $('<div>').addClass('option-buttons');
        options.forEach(function(option) {
            var button = $('<button>')
                .addClass('option-button')
                .text(option)
                .click(function() {
                    $(this).parent().remove();
                    handleUserInput(option);
                });
            buttonsDiv.append(button);
        });
        $('#chat-messages').append(buttonsDiv);
        $('#chat-messages').scrollTop($('#chat-messages')[0].scrollHeight);
    }

    function createMoodButtons(options) {
        var buttonsDiv = $('<div>').addClass('mood-buttons');
        options.forEach(function(option) {
            var button = $('<button>')
                .addClass('mood-button')
                .addClass(`mood-${option.toLowerCase()}`)
                .text(option)
                .click(function() {
                    $(this).parent().remove();
                    handleUserInput(option);
                });
            buttonsDiv.append(button);
        });
        $('#chat-messages').append(buttonsDiv);
    }

    function handleUserInput(message) {
        if (!message) {
            message = $('#userInput').val();
        }
        if (message.trim() === '') return;

        appendMessage(message, 'user');
        $('#userInput').val('');

        // Update user data based on current state
        switch(chatState) {
            case CHAT_STATES.NAME:
                userData.name = message;
                break;
            case CHAT_STATES.AGE:
                userData.age = message;
                break;
            case CHAT_STATES.OCCUPATION:
                userData.occupation = message;
                break;
            case CHAT_STATES.PAST_DIAGNOSIS:
                userData.pastDiagnosis = message;
                break;
            case CHAT_STATES.MOOD:
                userData.mood = message;
                break;
        }

        $.ajax({
            url: '/chat_message',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 
                message: message,
                chatState: chatState,
                userData: userData
            }),
            success: function(response) {
                if (response.message) {
                    appendMessage(response.message, 'bot');
                } else if (response.response) {
                    appendMessage(response.response, 'bot');
                }
                
                if (response.options && response.options.length > 0) {
                    createMoodButtons(response.options);
                }

                // Update chat state based on response type
                switch(response.type) {
                    case 'name_question':
                        chatState = CHAT_STATES.NAME;
                        break;
                    case 'age_question':
                        chatState = CHAT_STATES.AGE;
                        break;
                    case 'occupation_question':
                        chatState = CHAT_STATES.OCCUPATION;
                        break;
                    case 'diagnosis_question':
                        chatState = CHAT_STATES.PAST_DIAGNOSIS;
                        break;
                    case 'mood_question':
                        chatState = CHAT_STATES.MOOD;
                        break;
                    case 'mood_response':
                        chatState = CHAT_STATES.FREE_CHAT;
                        break;
                }
            },
            error: function(err) {
                console.error('Error:', err);
                appendMessage("I apologize, but I'm having trouble responding right now.", 'bot');
            }
        });
    }

    // Add function to update charts
    function updateMoodCharts(moodData) {
        if (moodData && moodData.length > 0) {
            // Update dashboard charts
            window.location.href = '/dashboard';
        }
    }

    function startAssessment() {
        $.ajax({
            url: '/start_assessment',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 
                startAssessment: true 
            }),
            success: function(response) {
                appendMessage(response.response, 'bot');
                if (response.options) {
                    createOptionButtons(response.options);
                }
            }
        });
    }

    // Handle send button click
    $('.send-button').click(function() {
        handleUserInput();
    });

    // Handle enter key press
    $('#userInput').keypress(function(e) {
        if (e.which == 13) {
            handleUserInput();
        }
    });

    // Initialize profile section
    function updateDateTime() {
        const now = new Date();
        const options = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        $('#currentDateTime').text(now.toLocaleDateString('en-US', options));
    }

    function initializeProfile() {
        // Get username from server
        $.get('/get_user_info', function(data) {
            $('#profileUsername').text(data.username);
        });
        
        // Get daily quote
        $.get('/get_daily_quote', function(data) {
            $('.quote-text').text(data.quote);
        });

        // Update date/time
        updateDateTime();
        setInterval(updateDateTime, 60000); // Update every minute
    }

    initializeProfile();

    // Modified initial greeting
    appendMessage("Hi! What's your name?", 'bot-name');
    chatState = 'name';
});
