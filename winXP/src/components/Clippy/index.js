import React, { useState } from 'react';
import styled from 'styled-components';
import clippyIcon from 'assets/windowsIcons/clippy.png';
import API_URL from '../../config';

const ClippyAssistant = ({ onClose }) => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [showSidebar, setShowSidebar] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Initialize with a new session on mount
  React.useEffect(() => {
    createNewSession();
    loadSessions();
  }, []);

  const createNewSession = async () => {
    try {
      const response = await fetch(`${API_URL}/api/sessions/new`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: 'New Chat' })
      });
      const data = await response.json();
      if (data.success) {
        setCurrentSessionId(data.session_id);
        setMessages([{ type: 'clippy', text: "Hi! I'm Clippy, your office assistant. How can I help you today?" }]);
        loadSessions();
      }
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };

  const loadSessions = async () => {
    try {
      const response = await fetch(`${API_URL}/api/sessions`);
      const data = await response.json();
      if (data.success) {
        setSessions(data.sessions);
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const loadSession = async (sessionId) => {
    try {
      const response = await fetch(`${API_URL}/api/sessions/${sessionId}`);
      const data = await response.json();
      if (data.success) {
        setCurrentSessionId(sessionId);
        setMessages(data.messages.map(m => ({
          type: m.sender === 'user' ? 'user' : 'clippy',
          text: m.message
        })));
        setShowSidebar(false);
      }
    } catch (error) {
      console.error('Error loading session:', error);
    }
  };

  const deleteSession = async (sessionId, e) => {
    e.stopPropagation();
    try {
      await fetch(`${API_URL}/api/sessions/${sessionId}`, { method: 'DELETE' });
      if (sessionId === currentSessionId) {
        createNewSession();
      }
      loadSessions();
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!inputText.trim() || !currentSessionId || isLoading) return;

    const userMessage = inputText;
    const newMessages = [...messages, { type: 'user', text: userMessage }];
    setMessages(newMessages);
    setInputText('');
    setIsLoading(true);
    
    const loadingMessages = [...newMessages, { type: 'clippy', text: 'Thinking...' }];
    setMessages(loadingMessages);
    
    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: userMessage,
          session_id: currentSessionId 
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        const finalMessages = [...newMessages, { type: 'clippy', text: data.response }];
        setMessages(finalMessages);
      } else {
        const errorMessages = [...newMessages, { type: 'clippy', text: "Sorry, I'm having trouble processing that. Please try again." }];
        setMessages(errorMessages);
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessages = [...newMessages, { type: 'clippy', text: "I'm having trouble connecting to my brain right now. Please make sure the backend server is running on port 8001." }];
      setMessages(errorMessages);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <ChatWindow>
      <TitleBar>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <MenuButton onClick={() => setShowSidebar(!showSidebar)}>☰</MenuButton>
          <TitleText>Clippy - Office Assistant</TitleText>
        </div>
        <div style={{ display: 'flex', gap: '4px' }}>
          <NewChatButton onClick={createNewSession}>+ New Chat</NewChatButton>
          <CloseButton onClick={onClose}>×</CloseButton>
        </div>
      </TitleBar>
      
      <ChatContainer>
        {showSidebar && (
          <Sidebar>
            <SidebarTitle>Chat History</SidebarTitle>
            <SessionsList>
              {sessions.map(session => (
                <SessionItem 
                  key={session.session_id}
                  active={session.session_id === currentSessionId}
                  onClick={() => loadSession(session.session_id)}
                >
                  <SessionTitle>{session.title}</SessionTitle>
                  <DeleteSessionBtn onClick={(e) => deleteSession(session.session_id, e)}>×</DeleteSessionBtn>
                </SessionItem>
              ))}
            </SessionsList>
          </Sidebar>
        )}
        
        <ChatContent>
          <MessagesContainer>
            {messages.map((message, index) => (
              <Message key={index} isClippy={message.type === 'clippy'}>
                <MessageBubble isClippy={message.type === 'clippy'}>
                  {message.text}
                </MessageBubble>
              </Message>
            ))}
          </MessagesContainer>
          
          <InputContainer>
            <ChatInput
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type a message..."
              disabled={isLoading}
            />
            <SendButton onClick={handleSendMessage} disabled={isLoading}>Send</SendButton>
          </InputContainer>
        </ChatContent>
      </ChatContainer>
    </ChatWindow>
  );
};

const Clippy = () => {
  const [showChat, setShowChat] = useState(false);

  return (
    <>
      <ClippyIcon onClick={() => setShowChat(true)}>
        <img 
          src={clippyIcon} 
          alt="Clippy" 
          draggable={false}
        />
      </ClippyIcon>
      
      {showChat && (
        <ClippyAssistant onClose={() => setShowChat(false)} />
      )}
    </>
  );
};

const ClippyIcon = styled.div`
  position: fixed;
  bottom: -50px;
  right: -20px;
  width: 300px;
  height: 360px;
  cursor: pointer;
  z-index: 9999;
  animation: bounce 2s ease-in-out infinite;
  pointer-events: auto;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    filter: drop-shadow(4px 4px 8px rgba(0,0,0,0.5));
  }
  
  &:hover {
    animation-play-state: paused;
    transform: scale(1.15) translateY(-10px);
  }
  
  transition: transform 0.3s ease;
  
  @keyframes bounce {
    0%, 100% {
      transform: translateY(0px);
    }
    50% {
      transform: translateY(-20px);
    }
  }
`;

const ChatWindow = styled.div`
  position: fixed;
  bottom: 80px;
  right: 220px;
  width: 650px;
  height: 520px;
  background: #ECE9D8;
  border: 3px outset #ECE9D8;
  border-radius: 8px 8px 0 0;
  box-shadow: 4px 4px 12px rgba(0,0,0,0.4);
  z-index: 10000;
  display: flex;
  flex-direction: column;
  font-family: 'Tahoma', sans-serif;
  pointer-events: auto;
`;

const ChatContainer = styled.div`
  display: flex;
  flex: 1;
  overflow: hidden;
`;

const TitleBar = styled.div`
  background: linear-gradient(to bottom, #0831d9 0%, #3593ff 4%, #288eff 6%, #127dff 8%, #036ffc 10%, #0262ee 14%, #0057e5 20%, #0054e3 24%, #0055eb 56%, #005bf5 66%, #026afe 76%, #0062ef 86%, #0052d6 92%, #0040ab 94%, #003092 100%);
  color: white;
  padding: 6px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 6px 6px 0 0;
  font-size: 12px;
  font-weight: bold;
  border-bottom: 1px solid #1f4788;
`;

const TitleText = styled.span`
  font-family: 'Tahoma', sans-serif;
  display: flex;
  align-items: center;
  gap: 6px;
  
  &:before {
    content: '';
    width: 16px;
    height: 16px;
    background: url(${clippyIcon});
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
  }
`;

const MenuButton = styled.button`
  background: linear-gradient(to bottom, #ECE9D8 0%, #D4D0C8 50%, #ECE9D8 100%);
  border: 2px outset #ECE9D8;
  color: #000;
  width: 24px;
  height: 22px;
  font-size: 14px;
  cursor: pointer;
  border-radius: 2px;
  
  &:hover {
    background: linear-gradient(to bottom, #F4F1E8 0%, #E4E0D8 50%, #F4F1E8 100%);
  }
  
  &:active {
    border: 2px inset #ECE9D8;
  }
`;

const NewChatButton = styled.button`
  background: linear-gradient(to bottom, #ECE9D8 0%, #D4D0C8 50%, #ECE9D8 100%);
  border: 2px outset #ECE9D8;
  padding: 2px 8px;
  font-size: 11px;
  font-family: 'Tahoma', sans-serif;
  cursor: pointer;
  border-radius: 2px;
  color: #000;
  
  &:hover {
    background: linear-gradient(to bottom, #F4F1E8 0%, #E4E0D8 50%, #F4F1E8 100%);
  }
  
  &:active {
    border: 2px inset #ECE9D8;
  }
`;

const CloseButton = styled.button`
  background: linear-gradient(to bottom, #ff6b6b 0%, #ee5a52 50%, #ff4444 100%);
  border: 1px outset #ff6b6b;
  color: white;
  width: 20px;
  height: 18px;
  font-size: 12px;
  font-weight: bold;
  line-height: 1;
  cursor: pointer;
  border-radius: 2px;
  
  &:hover {
    background: linear-gradient(to bottom, #ff7b7b 0%, #fe6a62 50%, #ff5555 100%);
  }
  
  &:active {
    border: 1px inset #ff6b6b;
    background: linear-gradient(to bottom, #ee5555 0%, #dd4444 50%, #cc3333 100%);
  }
`;

const Sidebar = styled.div`
  width: 200px;
  background: #D4D0C8;
  border-right: 2px inset #ECE9D8;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
`;

const SidebarTitle = styled.div`
  padding: 8px;
  font-size: 11px;
  font-weight: bold;
  background: #ECE9D8;
  border-bottom: 1px solid #999;
`;

const SessionsList = styled.div`
  flex: 1;
  overflow-y: auto;
`;

const SessionItem = styled.div`
  padding: 8px;
  font-size: 11px;
  cursor: pointer;
  background: ${props => props.active ? '#3593ff' : 'transparent'};
  color: ${props => props.active ? 'white' : '#000'};
  border-bottom: 1px solid #999;
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  &:hover {
    background: ${props => props.active ? '#3593ff' : '#E4E0D8'};
  }
`;

const SessionTitle = styled.span`
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const DeleteSessionBtn = styled.button`
  background: transparent;
  border: none;
  color: inherit;
  font-size: 16px;
  cursor: pointer;
  padding: 0 4px;
  
  &:hover {
    background: rgba(255,0,0,0.3);
  }
`;

const ChatContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 12px;
  background: #ECE9D8;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  margin-bottom: 12px;
  padding: 8px;
  background: white;
  border: 2px inset #ECE9D8;
  border-radius: 2px;
  max-height: 380px;
  
  &::-webkit-scrollbar {
    width: 16px;
  }
  
  &::-webkit-scrollbar-track {
    background: #ECE9D8;
    border: 1px inset #ECE9D8;
  }
  
  &::-webkit-scrollbar-thumb {
    background: linear-gradient(to bottom, #D4D0C8 0%, #ACA899 50%, #D4D0C8 100%);
    border: 1px outset #D4D0C8;
  }
  
  &::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(to bottom, #E4E0D8 0%, #BCA8A9 50%, #E4E0D8 100%);
  }
`;

const Message = styled.div`
  margin: 12px 0;
  display: flex;
  justify-content: ${props => props.isClippy ? 'flex-start' : 'flex-end'};
`;

const MessageBubble = styled.div`
  background: ${props => props.isClippy ? '#F8F8F8' : '#D4E7FF'};
  border: 2px ${props => props.isClippy ? 'inset' : 'outset'} ${props => props.isClippy ? '#E0E0E0' : '#8BB8FF'};
  border-radius: 4px;
  padding: 8px 12px;
  max-width: 280px;
  font-size: 12px;
  font-family: 'Tahoma', sans-serif;
  line-height: 1.4;
  box-shadow: 1px 1px 2px rgba(0,0,0,0.1);
`;

const InputContainer = styled.div`
  display: flex;
  gap: 8px;
  align-items: center;
`;

const ChatInput = styled.input`
  flex: 1;
  padding: 6px 8px;
  border: 2px inset #ECE9D8;
  border-radius: 2px;
  font-size: 12px;
  font-family: 'Tahoma', sans-serif;
  background: white;
  
  &:focus {
    outline: none;
    background: #FFFFCC;
  }
`;

const SendButton = styled.button`
  background: linear-gradient(to bottom, #ECE9D8 0%, #D4D0C8 50%, #ECE9D8 100%);
  border: 2px outset #ECE9D8;
  padding: 6px 16px;
  font-size: 12px;
  font-family: 'Tahoma', sans-serif;
  font-weight: normal;
  cursor: pointer;
  border-radius: 2px;
  min-width: 60px;
  
  &:hover {
    background: linear-gradient(to bottom, #F4F1E8 0%, #E4E0D8 50%, #F4F1E8 100%);
  }
  
  &:active {
    border: 2px inset #ECE9D8;
    background: linear-gradient(to bottom, #D4D0C8 0%, #C4C0B8 50%, #D4D0C8 100%);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: default;
  }
`;

export default Clippy;